"""Approval-scoped email operations with durable effect fencing."""
from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
import hashlib
from itertools import islice
import json
import re
from typing import Protocol

from jarvis_v2.backend import EffectJournal, EffectJournalError


EMAIL_READ_SCOPE = "email:read"
EMAIL_DRAFT_SCOPE = "email:draft"
EMAIL_SEND_SCOPE = "email:send"
MAX_SEARCH_RESULTS = 100
MAX_RECIPIENTS = 32
MAX_QUERY_BYTES = 512
MAX_SUBJECT_BYTES = 256
MAX_BODY_BYTES = 64 * 1024
MAX_REFERENCE_BYTES = 256
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


class EmailError(ValueError):
    """Raised when an email operation cannot be safely completed."""


class EmailAuthorizationError(EmailError):
    """Raised when a required email scope or owner decision is absent."""


class EmailReconciliationRequired(EmailError):
    """Raised when a prior external operation may have happened."""


class EmailTimeout(EmailError):
    """Raised without retrying an external operation whose result is unknown."""


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise EmailError(f"invalid {label}")
    return value


def _text(value: str, label: str, maximum: int, *, required: bool = True) -> str:
    if not isinstance(value, str) or (required and not value.strip()):
        raise EmailError(f"invalid {label}")
    if len(value.encode("utf-8")) > maximum:
        raise EmailError(f"{label} is outside the bounded range")
    if any(ord(char) < 32 and char not in "\t\n" for char in value):
        raise EmailError(f"{label} contains control data")
    return value


def _recipients(values: Sequence[str]) -> tuple[str, ...]:
    if isinstance(values, (str, bytes, Mapping)):
        raise EmailError("recipients must be a collection")
    try:
        normalized = tuple(values)
    except TypeError as exc:
        raise EmailError("recipients must be a collection") from exc
    if not 1 <= len(normalized) <= MAX_RECIPIENTS or len(set(normalized)) != len(normalized):
        raise EmailError("recipient count is outside the bounded range")
    checked: list[str] = []
    for value in normalized:
        if not isinstance(value, str) or "@" not in value or any(char.isspace() for char in value):
            raise EmailError("invalid recipient")
        checked.append(_text(value, "recipient", MAX_REFERENCE_BYTES))
    return tuple(checked)


def _payload_sha(message: "EmailMessage") -> str:
    payload = json.dumps(
        {"recipients": message.recipients, "subject": message.subject, "body": message.body},
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EmailMessage:
    recipients: tuple[str, ...]
    subject: str
    body: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "recipients", _recipients(self.recipients))
        object.__setattr__(self, "subject", _text(self.subject, "subject", MAX_SUBJECT_BYTES))
        object.__setattr__(
            self, "body", _text(self.body, "body", MAX_BODY_BYTES, required=False)
        )

    @property
    def payload_sha256(self) -> str:
        return _payload_sha(self)


@dataclass(frozen=True)
class EmailSummary:
    """Bounded search metadata; message bodies never enter search results."""

    message_id: str
    sender: str
    subject: str
    received_at: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "message_id", _identifier(self.message_id, "message id"))
        object.__setattr__(self, "sender", _text(self.sender, "sender", MAX_REFERENCE_BYTES))
        object.__setattr__(self, "subject", _text(self.subject, "subject", MAX_SUBJECT_BYTES))
        object.__setattr__(
            self, "received_at", _text(self.received_at, "received timestamp", MAX_REFERENCE_BYTES)
        )

    def model_context(self) -> dict[str, str]:
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "subject": self.subject,
            "received_at": self.received_at,
        }


@dataclass(frozen=True)
class EmailReceipt:
    request_id: str
    operation: str
    status: str
    provider_ref: str
    payload_sha256: str

    def model_context(self) -> dict[str, str]:
        return {
            "request_id": self.request_id,
            "operation": self.operation,
            "status": self.status,
            "provider_ref": self.provider_ref,
            "payload_sha256": self.payload_sha256,
        }


class EmailAdapter(Protocol):
    """Authenticated provider boundary; credentials stay inside the adapter."""

    def search(self, query: str, *, limit: int) -> Sequence[EmailSummary]: ...

    def create_draft(self, draft_id: str, message: EmailMessage) -> str: ...

    def send(self, send_id: str, message: EmailMessage) -> str: ...


class EmailService:
    """Search, draft and send through a scoped adapter and durable effect journal."""

    def __init__(
        self,
        database: str,
        adapter: EmailAdapter,
        authorize: Callable[[str, str], bool],
        *,
        task_id: str = "RUN-015",
        mailbox: str = "primary",
    ) -> None:
        if not callable(authorize):
            raise EmailAuthorizationError("email approval checker is required")
        self.adapter = adapter
        self._authorize = authorize
        self.task_id = _identifier(task_id, "task id")
        self.mailbox = _text(mailbox, "mailbox", MAX_REFERENCE_BYTES)
        self.journal = EffectJournal(database)

    def __enter__(self) -> "EmailService":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def search(self, query: str, *, limit: int = MAX_SEARCH_RESULTS) -> tuple[EmailSummary, ...]:
        query = _text(query, "search query", MAX_QUERY_BYTES)
        if type(limit) is not int or not 1 <= limit <= MAX_SEARCH_RESULTS:
            raise EmailError("search limit is outside the bounded range")
        self._require(EMAIL_READ_SCOPE, hashlib.sha256(query.encode()).hexdigest())
        try:
            result = self.adapter.search(query, limit=limit)
            if isinstance(result, (str, bytes, Mapping)):
                raise EmailError("email adapter returned an invalid search result")
            summaries = tuple(islice(iter(result), limit + 1))
        except TypeError as exc:
            raise EmailError("email adapter returned an invalid search result") from exc
        except EmailError:
            raise
        except Exception as exc:
            raise EmailError("email search failed") from exc
        if len(summaries) > limit:
            raise EmailError("email adapter returned too many results")
        return tuple(self._summary(item) for item in summaries)

    def create_draft(
        self, draft_id: str, recipients: Sequence[str], subject: str, body: str
    ) -> EmailReceipt:
        draft_id = _identifier(draft_id, "draft id")
        message = EmailMessage(tuple(recipients), subject, body)
        self._require(EMAIL_DRAFT_SCOPE, message.payload_sha256)
        return self._execute(
            draft_id,
            "email.draft",
            message.payload_sha256,
            lambda: self.adapter.create_draft(draft_id, message),
        )

    draft = create_draft

    def send(
        self,
        send_id: str,
        recipients: Sequence[str],
        subject: str,
        body: str,
        *,
        owner_approved: bool = False,
    ) -> EmailReceipt:
        send_id = _identifier(send_id, "send id")
        if type(owner_approved) is not bool or not owner_approved:
            raise EmailAuthorizationError("explicit owner approval is required for send")
        message = EmailMessage(tuple(recipients), subject, body)
        self._require(EMAIL_SEND_SCOPE, message.payload_sha256)
        return self._execute(
            send_id,
            "email.send",
            message.payload_sha256,
            lambda: self.adapter.send(send_id, message),
        )

    def reconcile(self) -> list[dict[str, object]]:
        return self.journal.reconcile_pending()

    def _require(self, scope: str, payload_sha256: str) -> None:
        try:
            allowed = self._authorize(scope, payload_sha256)
        except Exception as exc:
            raise EmailAuthorizationError("email approval check failed") from exc
        if allowed is not True:
            raise EmailAuthorizationError("email approval scope denied")

    def _execute(
        self,
        request_id: str,
        operation: str,
        payload_sha256: str,
        call: Callable[[], str],
    ) -> EmailReceipt:
        try:
            effect = self.journal.prepare(
                request_id,
                self.task_id,
                operation=operation,
                target=self.mailbox,
                request={"payload_sha256": payload_sha256},
            )
        except EffectJournalError as exc:
            raise EmailError("email effect journal rejected the request") from exc
        if not effect["execution_permitted"]:
            if effect["status"] == "needs_reconciliation":
                raise EmailReconciliationRequired("email effect requires reconciliation")
            return self._receipt(effect, request_id, operation, payload_sha256)
        try:
            provider_ref = _text(call(), "provider receipt", MAX_REFERENCE_BYTES)
        except TimeoutError as exc:
            raise EmailTimeout("email operation timed out; reconcile before retry") from exc
        except Exception as exc:
            self.journal.fail(request_id, {"error": "adapter_failed"})
            raise EmailError("email adapter operation failed") from exc
        try:
            completed = self.journal.complete(
                request_id, {"payload_sha256": payload_sha256, "provider_ref": provider_ref}
            )
        except EffectJournalError as exc:
            raise EmailError("email receipt persistence failed") from exc
        return self._receipt(completed, request_id, operation, payload_sha256)

    @staticmethod
    def _summary(value: object) -> EmailSummary:
        if not isinstance(value, EmailSummary):
            raise EmailError("email adapter returned an invalid summary")
        return value

    @staticmethod
    def _receipt(
        effect: Mapping[str, object], request_id: str, operation: str, payload_sha256: str
    ) -> EmailReceipt:
        result = effect.get("result")
        if not isinstance(result, Mapping):
            raise EmailError("stored email receipt is invalid")
        provider_ref = result.get("provider_ref", "")
        if not isinstance(provider_ref, str):
            raise EmailError("stored email receipt is invalid")
        return EmailReceipt(
            request_id=request_id,
            operation=operation,
            status=str(effect.get("status", "unknown")),
            provider_ref=provider_ref,
            payload_sha256=payload_sha256,
        )

    def close(self) -> None:
        self.journal.close()


EmailConnector = EmailService


__all__ = [
    "EMAIL_DRAFT_SCOPE",
    "EMAIL_READ_SCOPE",
    "EMAIL_SEND_SCOPE",
    "EmailAdapter",
    "EmailAuthorizationError",
    "EmailConnector",
    "EmailError",
    "EmailMessage",
    "EmailReceipt",
    "EmailReconciliationRequired",
    "EmailService",
    "EmailSummary",
    "EmailTimeout",
    "MAX_SEARCH_RESULTS",
]
