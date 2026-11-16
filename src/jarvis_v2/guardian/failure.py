"""Bounded Guardian failure classification and root-cause correlation."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
import re
from typing import Any

from .health import ProbeResult


MAX_EVIDENCE_REFS = 16
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")


class FailureClassificationError(ValueError):
    """Raised when failure observations are malformed."""


@dataclass(frozen=True)
class FailureAssessment:
    """Evidence-backed classification with no raw diagnostic payload."""

    component_id: str
    category: str
    severity: str
    root_cause: str
    component: ProbeResult
    dependencies: tuple[tuple[str, ProbeResult], ...]
    host: ProbeResult | None
    evidence_refs: tuple[str, ...]
    evidence_complete: bool

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["component"] = self.component.as_dict()
        result["dependencies"] = {
            name: observation.as_dict() for name, observation in self.dependencies
        }
        result["host"] = self.host.as_dict() if self.host is not None else None
        result["evidence_refs"] = list(self.evidence_refs)
        return result


class FailureClassifier:
    """Classify failures from bounded component, dependency and host probes."""

    def classify(
        self,
        component_id: str,
        *,
        component: ProbeResult,
        dependencies: Mapping[str, ProbeResult | bool] | None = None,
        host: ProbeResult | bool | None = None,
        evidence_refs: Iterable[str] = (),
    ) -> FailureAssessment:
        component_id = _identifier(component_id, "component id")
        if not isinstance(component, ProbeResult):
            raise FailureClassificationError("component observation is required")
        normalized_dependencies = _dependencies(dependencies)
        normalized_host = _observation(host, allow_none=True)
        refs = _references(evidence_refs)

        unknown_dependencies = tuple(
            name for name, observation in normalized_dependencies
            if observation.reason in {"unknown", "not_checked"}
        )
        failed_dependencies = tuple(
            name for name, observation in normalized_dependencies
            if not observation.ok and name not in unknown_dependencies
        )

        if normalized_host is not None and not normalized_host.ok:
            category, severity, root = "host_outage", "critical", "host"
        elif unknown_dependencies or normalized_host is None:
            category, severity, root = "unknown", "warning", "unknown"
        elif failed_dependencies:
            category, severity, root = "dependency_outage", "high", failed_dependencies[0]
        elif not component.ok and normalized_host is not None and normalized_host.ok and not unknown_dependencies:
            category, severity, root = "component_failure", "high", component_id
        elif component.ok and normalized_host is not None and normalized_host.ok and not unknown_dependencies:
            category, severity, root = "healthy", "none", "none"
        else:
            category, severity, root = "unknown", "warning", "unknown"

        return FailureAssessment(
            component_id=component_id,
            category=category,
            severity=severity,
            root_cause=root,
            component=component,
            dependencies=normalized_dependencies,
            host=normalized_host,
            evidence_refs=refs,
            evidence_complete=bool(refs),
        )


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise FailureClassificationError(f"invalid {label}")
    return value


def _observation(value: ProbeResult | bool | None, *, allow_none: bool = False) -> ProbeResult | None:
    if value is None and allow_none:
        return None
    if isinstance(value, ProbeResult):
        return value
    if type(value) is bool:
        return ProbeResult(ok=value, reason="healthy" if value else "failed")
    raise FailureClassificationError("observation is invalid")


def _dependencies(values: Mapping[str, ProbeResult | bool] | None) -> tuple[tuple[str, ProbeResult], ...]:
    if values is None:
        return ()
    if not isinstance(values, Mapping) or len(values) > MAX_EVIDENCE_REFS:
        raise FailureClassificationError("dependencies are invalid")
    normalized = [(_identifier(name, "dependency name"), _observation(value)) for name, value in values.items()]
    if len({name for name, _ in normalized}) != len(normalized):
        raise FailureClassificationError("dependencies must be unique")
    return tuple(sorted(normalized))


def _references(values: Iterable[str]) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise FailureClassificationError("evidence references must be a collection")
    try:
        normalized = tuple(values)
    except TypeError as exc:
        raise FailureClassificationError("evidence references must be iterable") from exc
    try:
        unique = len(normalized) == len(set(normalized))
    except TypeError as exc:
        raise FailureClassificationError("evidence references are invalid") from exc
    if len(normalized) > MAX_EVIDENCE_REFS or not unique:
        raise FailureClassificationError("evidence references are invalid")
    return tuple(_identifier(value, "evidence reference") for value in normalized)


__all__ = ["FailureAssessment", "FailureClassificationError", "FailureClassifier"]
