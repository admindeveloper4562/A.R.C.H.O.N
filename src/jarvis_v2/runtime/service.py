"""Authenticated Runtime boundary over the existing Core and Backend stores."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import re
from typing import Any

from jarvis_v2.backend.authorization import AuthorizationServer
from jarvis_v2.backend.event_bus import EventBus, EventBusError
from jarvis_v2.core.dispatch import DispatchError, DispatchStore
from jarvis_v2.core.registry import CoreRegistryError, ModuleRegistry


RUNTIME_MODULE = "runtime"
RUNTIME_READ_SCOPE = "runtime:read"
RUNTIME_HEALTH_SCOPE = "runtime:health"
_DISPATCH_PATH = re.compile(r"^/tasks/([A-Za-z0-9_.:-]{1,128})/(claim|ack)$")
_MAX_EVENTS = 100


class RuntimeServiceError(ValueError):
    """Raised for malformed Runtime boundary input."""


@dataclass(frozen=True)
class RuntimeResponse:
    """Small transport-neutral response used by local adapters and tests."""

    status: int
    body: Mapping[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {"status": self.status, "body": dict(self.body)}


class RuntimeService:
    """Expose authenticated Runtime operations without owning a web server."""

    def __init__(
        self,
        registry: ModuleRegistry,
        authorization: AuthorizationServer,
        dispatch: DispatchStore,
        events: EventBus,
    ) -> None:
        if not isinstance(registry, ModuleRegistry):
            raise RuntimeServiceError("module registry is required")
        try:
            registry.resolve(RUNTIME_MODULE)
        except CoreRegistryError as exc:
            raise RuntimeServiceError("runtime module is unavailable") from exc
        self.registry = registry
        self.authorization = authorization
        self.dispatch = dispatch
        self.events = events

    def handle(self, request: Mapping[str, Any]) -> RuntimeResponse:
        """Handle one bounded request and return a redacted deterministic result."""
        try:
            method, path, identity_id, scope = self._request_identity(request)
        except RuntimeServiceError:
            return RuntimeResponse(400, {"error": "invalid_request"})

        if method == "GET" and path == "/health":
            if not self._authorized(identity_id, scope, RUNTIME_HEALTH_SCOPE):
                return self._auth_failure(identity_id)
            return RuntimeResponse(200, {
                "module": RUNTIME_MODULE,
                "status": "ok",
                "scope": RUNTIME_HEALTH_SCOPE,
            })

        if method == "POST" and path == "/tasks":
            if not self._authorized(identity_id, scope, RUNTIME_READ_SCOPE):
                return self._auth_failure(identity_id)
            return self._create_task(request)

        if method == "GET" and path == "/events":
            if not self._authorized(identity_id, scope, RUNTIME_READ_SCOPE):
                return self._auth_failure(identity_id)
            return self._events(request)

        match = _DISPATCH_PATH.fullmatch(path)
        if match and method == "POST":
            if not self._authorized(identity_id, scope, RUNTIME_READ_SCOPE):
                return self._auth_failure(identity_id)
            if match.group(2) == "claim":
                return self._claim(request, match.group(1))
            return self._acknowledge(request, match.group(1))

        return RuntimeResponse(404 if path.startswith("/") else 400, {"error": "not_found"})

    def close(self) -> None:
        self.dispatch.close()
        self.events.close()

    def _create_task(self, request: Mapping[str, Any]) -> RuntimeResponse:
        body = self._body(request, {
            "task_id", "target_module", "scope", "acceptance", "correlation_id",
            "input_refs", "dispatch_id",
        })
        required = ("task_id", "target_module", "scope", "acceptance", "correlation_id")
        if any(key not in body for key in required):
            return RuntimeResponse(400, {"error": "invalid_task"})
        target = body["target_module"]
        try:
            capability = self.registry.resolve(target)
            scopes = self._scopes(body["scope"])
            if not set(scopes) <= capability.permission_scopes:
                return RuntimeResponse(403, {"error": "scope_denied"})
            dispatch = self.dispatch.create(
                body["task_id"], capability.key, scopes,
                body["acceptance"], correlation_id=body["correlation_id"],
                input_refs=body.get("input_refs", {}),
                dispatch_id=body.get("dispatch_id"),
            )
            event = self.events.publish(
                "task.handoff", RUNTIME_MODULE, dispatch["dispatch_id"], 1,
                {
                    "dispatch_id": dispatch["dispatch_id"],
                    "task_id": dispatch["task_id"],
                    "target_module": dispatch["target_module"],
                },
                correlation_id=dispatch["correlation_id"],
                idempotency_key=dispatch["dispatch_id"],
            )
        except (CoreRegistryError, DispatchError, EventBusError, RuntimeServiceError):
            return RuntimeResponse(400, {"error": "invalid_task"})
        return RuntimeResponse(201, {
            "dispatch": dispatch,
            "event_id": event.event_id,
        })

    def _events(self, request: Mapping[str, Any]) -> RuntimeResponse:
        try:
            consumer = request.get("consumer", "runtime-events")
            limit = request.get("limit", _MAX_EVENTS)
            if not isinstance(consumer, str) or not isinstance(limit, int):
                raise RuntimeServiceError("invalid event query")
            limit = max(1, min(limit, _MAX_EVENTS))
            events = self.events.pending(consumer, limit=limit)
        except (EventBusError, RuntimeServiceError):
            return RuntimeResponse(400, {"error": "invalid_event_query"})
        return RuntimeResponse(200, {
            "consumer": consumer,
            "events": [self._event_dict(event) for event in events],
        })

    def _claim(self, request: Mapping[str, Any], dispatch_id: str) -> RuntimeResponse:
        try:
            body = self._body(request, {"executor_id", "claim_id"})
            executor_id = body["executor_id"]
            if not isinstance(executor_id, str):
                raise RuntimeServiceError("invalid executor")
            claim = self.dispatch.claim(dispatch_id, executor_id, claim_id=body.get("claim_id"))
        except (DispatchError, RuntimeServiceError, KeyError):
            return RuntimeResponse(409, {"error": "dispatch_unavailable"})
        return RuntimeResponse(200, {"dispatch": claim})

    def _acknowledge(self, request: Mapping[str, Any], dispatch_id: str) -> RuntimeResponse:
        try:
            body = self._body(request, {"executor_id", "claim_id", "status", "result"})
            if any(key not in body for key in ("executor_id", "claim_id", "status", "result")):
                raise RuntimeServiceError("incomplete acknowledgement")
            if not isinstance(body["result"], Mapping):
                raise RuntimeServiceError("invalid result")
            acknowledged = self.dispatch.acknowledge(
                dispatch_id, body["executor_id"], body["claim_id"],
                status=body["status"], result=body["result"],
            )
        except (DispatchError, RuntimeServiceError, KeyError):
            return RuntimeResponse(409, {"error": "dispatch_acknowledgement_rejected"})
        return RuntimeResponse(200, {"dispatch": acknowledged})

    def _authorized(self, identity_id: str | None, scope: str | None, required: str) -> bool:
        return (
            isinstance(identity_id, str)
            and isinstance(scope, str)
            and scope == required
            and self.authorization.authorize(identity_id, RUNTIME_MODULE, required)
        )

    @staticmethod
    def _auth_failure(identity_id: str | None) -> RuntimeResponse:
        return RuntimeResponse(401 if not isinstance(identity_id, str) else 403, {"error": "access_denied"})

    @staticmethod
    def _request_identity(request: Mapping[str, Any]) -> tuple[str, str, str, str]:
        if not isinstance(request, Mapping):
            raise RuntimeServiceError("request must be an object")
        method = request.get("method")
        path = request.get("path")
        identity_id = request.get("identity_id")
        scope = request.get("scope")
        if any(not isinstance(value, str) or not value for value in (method, path, identity_id, scope)):
            raise RuntimeServiceError("request identity is incomplete")
        return method.upper(), path, identity_id, scope

    @staticmethod
    def _body(request: Mapping[str, Any], allowed: set[str]) -> Mapping[str, Any]:
        body = request.get("body", {})
        if not isinstance(body, Mapping) or not set(body) <= allowed:
            raise RuntimeServiceError("invalid request body")
        return body

    @staticmethod
    def _scopes(value: Any) -> tuple[str, ...]:
        values = (value,) if isinstance(value, str) else tuple(value) if isinstance(value, (list, tuple)) else ()
        if not values or any(not isinstance(item, str) or not item for item in values):
            raise RuntimeServiceError("invalid target scopes")
        if len(values) != len(set(values)):
            raise RuntimeServiceError("duplicate target scopes")
        return values

    @staticmethod
    def _event_dict(event: Any) -> dict[str, Any]:
        return {
            "schema": event.schema,
            "event_id": event.event_id,
            "event_type": event.event_type,
            "producer": event.producer,
            "aggregate_id": event.aggregate_id,
            "sequence": event.sequence,
            "correlation_id": event.correlation_id,
            "causation_id": event.causation_id,
            "privacy_scope": event.privacy_scope,
            "payload_hash": event.payload_hash,
            "payload": dict(event.payload),
            "idempotency_key": event.idempotency_key,
        }


__all__ = [
    "RUNTIME_HEALTH_SCOPE",
    "RUNTIME_MODULE",
    "RUNTIME_READ_SCOPE",
    "RuntimeResponse",
    "RuntimeService",
    "RuntimeServiceError",
]
