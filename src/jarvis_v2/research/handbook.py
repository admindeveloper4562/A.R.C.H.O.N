"""Proposal-only governance for Research development tips.

The workflow records an immutable, digest-bound proposal and its independent
review. It never edits ``CODING_HANDBOOK.md``; the serialized Merger owns that
side effect after the Master has accepted the receipts.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import re
from collections.abc import Mapping


CANONICAL_HANDBOOK_PATH = "CODING_HANDBOOK.md"
MAX_REASON_BYTES = 4096
MAX_EVIDENCE_BYTES = 2048
MAX_CANDIDATE_BYTES = 512 * 1024
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SECTIONS = frozenset({"constitution", "patterns", "mistakes", "tips"})
_ACTOR_ROLES = frozenset({"recovery", "guardian", "qc", "research", "owner"})
_REVIEWER_ROLES = frozenset({"qc", "research", "owner"})
_OPERATIONS = frozenset({"append", "supersede"})
_STATES = frozenset({
    "PROPOSED", "QC_PENDING", "APPROVED", "MERGE_QUEUED", "APPLIED",
    "VERIFIED", "REJECTED", "BLOCKED",
})


class HandbookGovernanceError(ValueError):
    """Raised when a handbook proposal or receipt fails closed validation."""


def sha256_text(value: str) -> str:
    """Return the digest of bounded UTF-8 text without interpreting it."""
    if not isinstance(value, str):
        raise HandbookGovernanceError("content must be text")
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise HandbookGovernanceError(f"invalid {label}")
    return value


def _sha(value: object, label: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value.lower()):
        raise HandbookGovernanceError(f"invalid {label}")
    return value.lower()


def _text(value: object, label: str, maximum: int, *, empty: bool = False) -> str:
    if (
        not isinstance(value, str)
        or (not empty and not value.strip())
        or len(value.encode("utf-8")) > maximum
        or any(ord(char) < 32 for char in value)
    ):
        raise HandbookGovernanceError(f"invalid {label}")
    return value


def _markdown(value: object) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or len(value.encode("utf-8")) > MAX_CANDIDATE_BYTES
        or any(ord(char) < 32 and char not in "\n\r\t" for char in value)
    ):
        raise HandbookGovernanceError("invalid handbook candidate")
    return value


def _timestamp(value: object, label: str) -> str:
    if not isinstance(value, str) or len(value.encode("utf-8")) > 64:
        raise HandbookGovernanceError(f"invalid {label}")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise HandbookGovernanceError(f"invalid {label}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise HandbookGovernanceError(f"invalid {label}")
    return value


def _strict_dict(data: object, expected: set[str], label: str) -> Mapping[str, object]:
    if not isinstance(data, Mapping) or set(data) != expected:
        raise HandbookGovernanceError(f"invalid {label} fields")
    return data


@dataclass(frozen=True)
class HandbookEditProposalV1:
    """Digest-bound proposal envelope; it grants no write permission."""

    proposal_id: str
    handbook_path: str
    base_digest: str
    candidate_digest: str
    section: str
    actor_role: str
    actor_id: str
    operation: str
    entry_id: str
    supersedes: str | None
    content_digest: str
    reason: str
    regression_evidence: str
    created_at_utc: str
    schema_version: int = 1

    def __post_init__(self) -> None:
        _identifier(self.proposal_id, "proposal id")
        if self.handbook_path != CANONICAL_HANDBOOK_PATH:
            raise HandbookGovernanceError("handbook path is not canonical")
        for value, label in (
            (self.base_digest, "base digest"),
            (self.candidate_digest, "candidate digest"),
            (self.content_digest, "content digest"),
        ):
            _sha(value, label)
        if self.section not in _SECTIONS:
            raise HandbookGovernanceError("invalid handbook section")
        if self.actor_role not in _ACTOR_ROLES:
            raise HandbookGovernanceError("invalid handbook actor role")
        _identifier(self.actor_id, "actor id")
        if self.operation not in _OPERATIONS:
            raise HandbookGovernanceError("invalid handbook operation")
        _identifier(self.entry_id, "entry id")
        if self.operation == "supersede":
            _identifier(self.supersedes, "superseded entry id")
        elif self.supersedes is not None:
            raise HandbookGovernanceError("append proposal cannot supersede an entry")
        _text(self.reason, "proposal reason", MAX_REASON_BYTES)
        _text(self.regression_evidence, "regression evidence", MAX_EVIDENCE_BYTES)
        _timestamp(self.created_at_utc, "creation timestamp")
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise HandbookGovernanceError("unsupported handbook proposal version")

    def as_dict(self) -> dict[str, object]:
        return {
            "proposal_id": self.proposal_id,
            "handbook_path": self.handbook_path,
            "base_digest": self.base_digest,
            "candidate_digest": self.candidate_digest,
            "section": self.section,
            "actor_role": self.actor_role,
            "actor_id": self.actor_id,
            "operation": self.operation,
            "entry_id": self.entry_id,
            "supersedes": self.supersedes,
            "content_digest": self.content_digest,
            "reason": self.reason,
            "regression_evidence": self.regression_evidence,
            "created_at_utc": self.created_at_utc,
            "schema_version": self.schema_version,
        }

    @classmethod
    def from_dict(cls, data: object) -> "HandbookEditProposalV1":
        fields = {
            "proposal_id", "handbook_path", "base_digest", "candidate_digest",
            "section", "actor_role", "actor_id", "operation", "entry_id",
            "supersedes", "content_digest", "reason", "regression_evidence",
            "created_at_utc", "schema_version",
        }
        values = _strict_dict(data, fields, "proposal")
        try:
            return cls(**values)  # type: ignore[arg-type]
        except TypeError as exc:
            raise HandbookGovernanceError("invalid proposal values") from exc


@dataclass(frozen=True)
class HandbookReviewReceipt:
    """Independent review bound to one exact proposal candidate."""

    receipt_id: str
    proposal_id: str
    candidate_digest: str
    reviewer_id: str
    reviewer_role: str
    decision: str
    evidence_ref: str
    reviewed_at_utc: str
    schema_version: int = 1

    def __post_init__(self) -> None:
        _identifier(self.receipt_id, "review receipt id")
        _identifier(self.proposal_id, "proposal id")
        _sha(self.candidate_digest, "review candidate digest")
        _identifier(self.reviewer_id, "reviewer id")
        if self.reviewer_role not in _REVIEWER_ROLES:
            raise HandbookGovernanceError("invalid reviewer role")
        if self.decision not in {"approved", "rejected"}:
            raise HandbookGovernanceError("invalid review decision")
        _text(self.evidence_ref, "review evidence", MAX_EVIDENCE_BYTES)
        _timestamp(self.reviewed_at_utc, "review timestamp")
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise HandbookGovernanceError("unsupported review version")

    def as_dict(self) -> dict[str, object]:
        return {
            "receipt_id": self.receipt_id,
            "proposal_id": self.proposal_id,
            "candidate_digest": self.candidate_digest,
            "reviewer_id": self.reviewer_id,
            "reviewer_role": self.reviewer_role,
            "decision": self.decision,
            "evidence_ref": self.evidence_ref,
            "reviewed_at_utc": self.reviewed_at_utc,
            "schema_version": self.schema_version,
        }


@dataclass(frozen=True)
class HandbookOwnerApproval:
    """Owner receipt required for constitutional/security proposals."""

    receipt_id: str
    proposal_id: str
    candidate_digest: str
    owner_id: str
    approved_at_utc: str

    def __post_init__(self) -> None:
        _identifier(self.receipt_id, "owner receipt id")
        _identifier(self.proposal_id, "proposal id")
        _sha(self.candidate_digest, "owner candidate digest")
        _identifier(self.owner_id, "owner id")
        _timestamp(self.approved_at_utc, "owner approval timestamp")

    def as_dict(self) -> dict[str, object]:
        return {
            "receipt_id": self.receipt_id,
            "proposal_id": self.proposal_id,
            "candidate_digest": self.candidate_digest,
            "owner_id": self.owner_id,
            "approved_at_utc": self.approved_at_utc,
        }


@dataclass(frozen=True)
class HandbookProposalRecord:
    proposal: HandbookEditProposalV1
    state: str
    review: HandbookReviewReceipt | None = None
    owner_approval: HandbookOwnerApproval | None = None
    merger_id: str | None = None

    def __post_init__(self) -> None:
        if self.state not in _STATES:
            raise HandbookGovernanceError("invalid proposal state")

    def as_dict(self) -> dict[str, object]:
        return {
            "proposal": self.proposal.as_dict(),
            "state": self.state,
            "review": None if self.review is None else self.review.as_dict(),
            "owner_approval": None if self.owner_approval is None else self.owner_approval.as_dict(),
            "merger_id": self.merger_id,
        }


@dataclass
class _StoredProposal:
    proposal: HandbookEditProposalV1
    state: str = "PROPOSED"
    review: HandbookReviewReceipt | None = None
    owner_approval: HandbookOwnerApproval | None = None
    merger_id: str | None = None

    def snapshot(self) -> HandbookProposalRecord:
        return HandbookProposalRecord(
            self.proposal, self.state, self.review, self.owner_approval, self.merger_id
        )


def _proposer_allowed(proposal: HandbookEditProposalV1) -> bool:
    if proposal.section == "tips":
        return proposal.actor_role == "research"
    if proposal.section == "mistakes":
        return proposal.actor_role in {"recovery", "guardian"}
    if proposal.section == "patterns":
        return proposal.actor_role in {"qc", "research", "owner"}
    return True


class HandbookProposalWorkflow:
    """In-memory proposal ledger for the Master/QC/Merger handoff.

    It deliberately has no filesystem or SQLite side effect. The canonical
    Master persists the receipt and the serialized Merger performs the actual
    handbook write after ``merge`` succeeds.
    """

    def __init__(self) -> None:
        self._records: dict[str, _StoredProposal] = {}

    def submit(
        self,
        proposal: HandbookEditProposalV1,
        *,
        candidate_content: str | None = None,
    ) -> HandbookProposalRecord:
        if not isinstance(proposal, HandbookEditProposalV1):
            raise HandbookGovernanceError("proposal is required")
        if not _proposer_allowed(proposal):
            raise HandbookGovernanceError("actor is not authorized for handbook section")
        if candidate_content is not None:
            candidate_content = _markdown(candidate_content)
            if sha256_text(candidate_content) != proposal.candidate_digest:
                raise HandbookGovernanceError("candidate digest does not match content")
        existing = self._records.get(proposal.proposal_id)
        if existing is not None:
            if existing.proposal != proposal:
                raise HandbookGovernanceError("conflicting proposal replay")
            return existing.snapshot()
        self._records[proposal.proposal_id] = _StoredProposal(proposal)
        return self._records[proposal.proposal_id].snapshot()

    def get(self, proposal_id: str) -> HandbookProposalRecord:
        _identifier(proposal_id, "proposal id")
        try:
            return self._records[proposal_id].snapshot()
        except KeyError as exc:
            raise HandbookGovernanceError("unknown proposal") from exc

    def review(
        self,
        proposal_id: str,
        receipt: HandbookReviewReceipt,
    ) -> HandbookProposalRecord:
        record = self._stored(proposal_id)
        if receipt.proposal_id != proposal_id or receipt.candidate_digest != record.proposal.candidate_digest:
            raise HandbookGovernanceError("review receipt is not bound to candidate")
        if receipt.reviewer_id == record.proposal.actor_id:
            raise HandbookGovernanceError("self approval is not permitted")
        if record.review is not None:
            if record.review == receipt:
                return record.snapshot()
            raise HandbookGovernanceError("conflicting review replay")
        if record.state not in {"PROPOSED", "QC_PENDING"}:
            raise HandbookGovernanceError("proposal is not reviewable")
        record.state = "APPROVED" if receipt.decision == "approved" else "REJECTED"
        record.review = receipt
        return record.snapshot()

    def owner_approve(self, proposal_id: str, approval: HandbookOwnerApproval) -> HandbookProposalRecord:
        record = self._stored(proposal_id)
        if approval.proposal_id != proposal_id or approval.candidate_digest != record.proposal.candidate_digest:
            raise HandbookGovernanceError("owner receipt is not bound to candidate")
        if approval.owner_id == record.proposal.actor_id:
            raise HandbookGovernanceError("self approval is not permitted")
        if record.owner_approval is not None:
            if record.owner_approval == approval:
                return record.snapshot()
            raise HandbookGovernanceError("conflicting owner approval replay")
        record.owner_approval = approval
        return record.snapshot()

    def queue_for_merge(self, proposal_id: str, *, current_base_digest: str) -> HandbookProposalRecord:
        record = self._stored(proposal_id)
        current_base_digest = _sha(current_base_digest, "current base digest")
        if record.state != "APPROVED":
            raise HandbookGovernanceError("independent approval is required")
        if current_base_digest != record.proposal.base_digest:
            record.state = "BLOCKED"
            raise HandbookGovernanceError("stale handbook base")
        if record.proposal.section == "constitution" and record.owner_approval is None:
            raise HandbookGovernanceError("owner approval is required")
        record.state = "MERGE_QUEUED"
        return record.snapshot()

    def merge(
        self,
        proposal_id: str,
        *,
        merger_id: str,
        current_base_digest: str,
        applied_candidate_digest: str,
    ) -> HandbookProposalRecord:
        record = self._stored(proposal_id)
        _identifier(merger_id, "merger id")
        if merger_id in {record.proposal.actor_id, record.review.reviewer_id if record.review else ""}:
            raise HandbookGovernanceError("serialized Merger must be independent")
        if record.state != "MERGE_QUEUED":
            raise HandbookGovernanceError("proposal is not queued for merge")
        if _sha(current_base_digest, "current base digest") != record.proposal.base_digest:
            record.state = "BLOCKED"
            raise HandbookGovernanceError("stale handbook base")
        if _sha(applied_candidate_digest, "applied candidate digest") != record.proposal.candidate_digest:
            raise HandbookGovernanceError("applied candidate is not the approved digest")
        record.merger_id = merger_id
        record.state = "VERIFIED"
        return record.snapshot()

    def _stored(self, proposal_id: str) -> _StoredProposal:
        _identifier(proposal_id, "proposal id")
        try:
            return self._records[proposal_id]
        except KeyError as exc:
            raise HandbookGovernanceError("unknown proposal") from exc


HandbookProposal = HandbookEditProposalV1
HandbookWorkflow = HandbookProposalWorkflow


__all__ = [
    "CANONICAL_HANDBOOK_PATH",
    "HandbookEditProposalV1",
    "HandbookGovernanceError",
    "HandbookOwnerApproval",
    "HandbookProposal",
    "HandbookProposalRecord",
    "HandbookProposalWorkflow",
    "HandbookReviewReceipt",
    "HandbookWorkflow",
    "sha256_text",
]
