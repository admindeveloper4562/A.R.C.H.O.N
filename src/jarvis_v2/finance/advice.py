"""Read-only, consent- and approval-aware finance advice records."""
from __future__ import annotations

from dataclasses import dataclass, replace

from .alerts import FinanceAlertService
from .ingestion import FinanceIngestionError, FinanceStore, _identifier, _text


class FinanceAdviceError(FinanceIngestionError):
    """Raised when an advice or notification transition is unsafe."""


@dataclass(frozen=True)
class FinanceRecommendation:
    recommendation_id: str
    source_id: str
    scope_id: str
    alert_id: str
    message: str
    status: str
    certainty: str = "advisory"
    approved: bool = False
    suppressed: bool = False

    def __post_init__(self) -> None:
        _identifier(self.recommendation_id, "recommendation id")
        _identifier(self.source_id, "source id")
        _identifier(self.scope_id, "scope id")
        _identifier(self.alert_id, "recommendation alert id")
        _text(self.message, "recommendation message")
        if self.status not in {"consent_required", "approval_required", "approved", "suppressed"}:
            raise FinanceAdviceError("recommendation status is invalid")
        if self.certainty != "advisory":
            raise FinanceAdviceError("recommendations must be advisory")
        if type(self.approved) is not bool or type(self.suppressed) is not bool:
            raise FinanceAdviceError("recommendation flags are invalid")
        if self.status == "approved" and not self.approved:
            raise FinanceAdviceError("approved recommendation is not marked approved")

    def approve(self, *, consent_granted: bool) -> "FinanceRecommendation":
        if not consent_granted:
            raise FinanceAdviceError("explicit read consent is required")
        if self.suppressed:
            raise FinanceAdviceError("suppressed recommendation cannot be approved")
        return replace(self, status="approved", approved=True)

    def suppress(self) -> "FinanceRecommendation":
        return replace(self, status="suppressed", suppressed=True, approved=False)

    def as_dict(self) -> dict[str, object]:
        return {
            "recommendation_id": self.recommendation_id,
            "source_id": self.source_id,
            "person_id": self.scope_id,
            "alert_id": self.alert_id,
            "message": self.message,
            "status": self.status,
            "certainty": self.certainty,
            "approved": self.approved,
            "suppressed": self.suppressed,
        }


@dataclass(frozen=True)
class FinanceNotification:
    notification_id: str
    recommendation_id: str
    source_id: str
    scope_id: str
    message: str
    status: str

    def __post_init__(self) -> None:
        _identifier(self.notification_id, "notification id")
        _identifier(self.recommendation_id, "notification recommendation id")
        _identifier(self.source_id, "source id")
        _identifier(self.scope_id, "scope id")
        _text(self.message, "notification message")
        if self.status not in {"consent_required", "approval_required", "ready", "suppressed"}:
            raise FinanceAdviceError("notification status is invalid")

    @property
    def deliverable(self) -> bool:
        return self.status == "ready"

    def as_dict(self) -> dict[str, object]:
        return {
            "notification_id": self.notification_id,
            "recommendation_id": self.recommendation_id,
            "source_id": self.source_id,
            "person_id": self.scope_id,
            "message": self.message,
            "status": self.status,
            "deliverable": self.deliverable,
        }


class FinanceAdviceService:
    """Create advice records without writing to Mira or delivering messages."""

    def __init__(self, store: FinanceStore):
        if not isinstance(store, FinanceStore):
            raise FinanceAdviceError("advice requires a FinanceStore")
        self.store = store
        self.alerts = FinanceAlertService(store)

    def recommendations(self, source_id: str, scope_id: str, *, consent_granted: bool = False) -> tuple[FinanceRecommendation, ...]:
        source_id = _identifier(source_id, "source id")
        scope_id = _identifier(scope_id, "scope id")
        result = []
        for alert in self.alerts.detect(source_id, scope_id):
            result.append(FinanceRecommendation(
                f"recommendation-{alert.alert_id}", source_id, scope_id, alert.alert_id,
                "A finance pattern is available for review; no action is required.",
                "approval_required" if consent_granted else "consent_required",
            ))
        return tuple(result)

    @staticmethod
    def notification(
        recommendation: FinanceRecommendation,
        *,
        consent_granted: bool = False,
    ) -> FinanceNotification:
        if not isinstance(recommendation, FinanceRecommendation):
            raise FinanceAdviceError("notification requires a recommendation")
        if recommendation.suppressed:
            status = "suppressed"
        elif not consent_granted:
            status = "consent_required"
        elif not recommendation.approved:
            status = "approval_required"
        else:
            status = "ready"
        return FinanceNotification(
            f"notification-{recommendation.recommendation_id}", recommendation.recommendation_id,
            recommendation.source_id, recommendation.scope_id, recommendation.message, status,
        )


__all__ = [
    "FinanceAdviceError",
    "FinanceAdviceService",
    "FinanceNotification",
    "FinanceRecommendation",
]
