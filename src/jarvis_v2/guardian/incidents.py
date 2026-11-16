"""Bounded Guardian incident deduplication, alert limiting and acknowledgment."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import re
from typing import Any

from .failure import FailureAssessment


MAX_INCIDENTS = 256
MAX_ALERTS_PER_INCIDENT = 16
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class IncidentTrackerError(ValueError):
    """Raised when an incident operation is invalid or exceeds its bound."""


@dataclass(frozen=True)
class IncidentRecord:
    """A deduplicated incident record containing identifiers, not raw logs."""

    fingerprint: str
    component_id: str
    category: str
    root_cause: str
    occurrences: int
    alerts_emitted: int
    acknowledged: bool
    evidence_refs: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["evidence_refs"] = list(self.evidence_refs)
        return result


@dataclass(frozen=True)
class IncidentNotice:
    """Result of recording one occurrence."""

    record: IncidentRecord
    new_incident: bool
    alert_emitted: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "record": self.record.as_dict(),
            "new_incident": self.new_incident,
            "alert_emitted": self.alert_emitted,
        }


class IncidentTracker:
    """Keep one bounded record per failure identity and limit its alerts."""

    def __init__(
        self,
        *,
        max_incidents: int = MAX_INCIDENTS,
        max_alerts_per_incident: int = 3,
    ) -> None:
        if type(max_incidents) is not int or not 1 <= max_incidents <= MAX_INCIDENTS:
            raise IncidentTrackerError("incident limit is invalid")
        if (
            type(max_alerts_per_incident) is not int
            or not 1 <= max_alerts_per_incident <= MAX_ALERTS_PER_INCIDENT
        ):
            raise IncidentTrackerError("alert limit is invalid")
        self._max_incidents = max_incidents
        self._max_alerts = max_alerts_per_incident
        self._records: dict[str, IncidentRecord] = {}

    @property
    def records(self) -> tuple[IncidentRecord, ...]:
        """Return a stable snapshot ordered by fingerprint."""
        return tuple(self._records[key] for key in sorted(self._records))

    def record(self, assessment: FailureAssessment) -> IncidentNotice:
        """Record one verified failure and emit at most the configured alerts."""
        if not isinstance(assessment, FailureAssessment):
            raise IncidentTrackerError("failure assessment is required")
        if assessment.category == "healthy":
            raise IncidentTrackerError("healthy assessment is not an incident")
        if not assessment.evidence_complete:
            raise IncidentTrackerError("incident evidence is incomplete")

        fingerprint = _fingerprint(assessment)
        existing = self._records.get(fingerprint)
        if existing is None:
            if len(self._records) >= self._max_incidents:
                raise IncidentTrackerError("incident limit reached")
            current = IncidentRecord(
                fingerprint=fingerprint,
                component_id=assessment.component_id,
                category=assessment.category,
                root_cause=assessment.root_cause,
                occurrences=0,
                alerts_emitted=0,
                acknowledged=False,
                evidence_refs=assessment.evidence_refs,
            )
            new_incident = True
        else:
            current = existing
            new_incident = False

        alert = not current.acknowledged and current.alerts_emitted < self._max_alerts
        updated = IncidentRecord(
            fingerprint=current.fingerprint,
            component_id=current.component_id,
            category=current.category,
            root_cause=current.root_cause,
            occurrences=current.occurrences + 1,
            alerts_emitted=current.alerts_emitted + int(alert),
            acknowledged=current.acknowledged,
            evidence_refs=current.evidence_refs,
        )
        self._records[fingerprint] = updated
        return IncidentNotice(updated, new_incident, alert)

    def acknowledge(self, fingerprint: str) -> IncidentRecord:
        """Acknowledge one incident without removing its history."""
        if not isinstance(fingerprint, str) or not _DIGEST.fullmatch(fingerprint):
            raise IncidentTrackerError("incident fingerprint is invalid")
        current = self._records.get(fingerprint)
        if current is None:
            raise IncidentTrackerError("incident not found")
        updated = IncidentRecord(
            fingerprint=current.fingerprint,
            component_id=current.component_id,
            category=current.category,
            root_cause=current.root_cause,
            occurrences=current.occurrences,
            alerts_emitted=current.alerts_emitted,
            acknowledged=True,
            evidence_refs=current.evidence_refs,
        )
        self._records[fingerprint] = updated
        return updated


def _fingerprint(assessment: FailureAssessment) -> str:
    payload = {
        "component_id": assessment.component_id,
        "category": assessment.category,
        "root_cause": assessment.root_cause,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


__all__ = ["IncidentNotice", "IncidentRecord", "IncidentTracker", "IncidentTrackerError"]
