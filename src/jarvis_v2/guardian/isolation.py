"""Deterministic smallest-unit drain, quiesce and isolation controls."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
import re
from typing import Any


MAX_COMPONENTS = 128
MAX_EFFECTS_PER_COMPONENT = 256
MAX_REASON_LENGTH = 256
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_STATES = frozenset({"running", "draining", "quiesced", "isolated"})
_EFFECT_STATES = frozenset({"in_flight", "completed", "failed", "unknown"})
_FINAL_EFFECT_STATES = frozenset({"completed", "failed", "unknown"})


class IsolationError(ValueError):
    """Raised when a module isolation transition is unsafe or malformed."""


@dataclass(frozen=True)
class EffectRecord:
    """Bounded effect state; evidence is a reference, never effect content."""

    effect_id: str
    status: str
    evidence_ref: str = ""

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class IsolationSnapshot:
    """Read-only state for one module and its bounded effect ledger."""

    component_id: str
    state: str
    generation: int
    reason: str
    effects: tuple[EffectRecord, ...]

    @property
    def in_flight(self) -> tuple[str, ...]:
        return tuple(
            effect.effect_id for effect in self.effects if effect.status == "in_flight"
        )

    @property
    def unresolved(self) -> tuple[str, ...]:
        return tuple(
            effect.effect_id
            for effect in self.effects
            if effect.status in {"in_flight", "unknown"}
        )

    @property
    def accepts_effects(self) -> bool:
        return self.state == "running"

    def as_dict(self) -> dict[str, Any]:
        return {
            "component_id": self.component_id,
            "state": self.state,
            "generation": self.generation,
            "reason": self.reason,
            "effects": [effect.as_dict() for effect in self.effects],
            "in_flight": list(self.in_flight),
            "unresolved": list(self.unresolved),
            "accepts_effects": self.accepts_effects,
        }


@dataclass
class _ComponentState:
    state: str = "running"
    generation: int = 0
    reason: str = ""
    effects: dict[str, EffectRecord] | None = None

    def __post_init__(self) -> None:
        if self.effects is None:
            self.effects = {}


class IsolationController:
    """Fence one failing module without stopping independent modules.

    The controller records effect identities only. Callers reconcile the
    durable effect journal before quiescing; this class never executes a
    process, network, Git or database operation.
    """

    def __init__(self, component_ids: Iterable[str] = ()) -> None:
        if isinstance(component_ids, (str, bytes)):
            raise IsolationError("component ids must be an iterable")
        try:
            values = tuple(component_ids)
        except TypeError as exc:
            raise IsolationError("component ids must be iterable") from exc
        if len(values) > MAX_COMPONENTS:
            raise IsolationError("component limit exceeded")
        self._components: dict[str, _ComponentState] = {}
        for component_id in values:
            self.register(component_id)

    def register(self, component_id: str) -> IsolationSnapshot:
        """Register one component; repeated identical registration is safe."""
        component_id = _identifier(component_id, "component id")
        existing = self._components.get(component_id)
        if existing is None:
            if len(self._components) >= MAX_COMPONENTS:
                raise IsolationError("component limit exceeded")
            existing = _ComponentState()
            self._components[component_id] = existing
        return self.snapshot(component_id)

    def snapshot(self, component_id: str) -> IsolationSnapshot:
        component_id = _identifier(component_id, "component id")
        state = self._component(component_id)
        return IsolationSnapshot(
            component_id=component_id,
            state=state.state,
            generation=state.generation,
            reason=state.reason,
            effects=tuple(state.effects[key] for key in sorted(state.effects)),
        )

    def can_accept_effect(self, component_id: str) -> bool:
        return self.snapshot(component_id).accepts_effects

    def begin_effect(self, component_id: str, effect_id: str) -> IsolationSnapshot:
        """Record an effect before execution while the module is running."""
        component_id = _identifier(component_id, "component id")
        effect_id = _identifier(effect_id, "effect id")
        state = self._component(component_id)
        if state.state != "running":
            raise IsolationError("component is not accepting new effects")
        if effect_id in state.effects:
            raise IsolationError("effect identity already recorded")
        if len(state.effects) >= MAX_EFFECTS_PER_COMPONENT:
            raise IsolationError("effect history limit reached")
        state.effects[effect_id] = EffectRecord(effect_id, "in_flight")
        return self.snapshot(component_id)

    start_effect = begin_effect

    def complete_effect(
        self,
        component_id: str,
        effect_id: str,
        *,
        status: str = "completed",
        evidence_ref: str = "",
        generation: int | None = None,
    ) -> IsolationSnapshot:
        """Finalize one effect without reopening a fenced module."""
        return self.reconcile_effect(
            component_id,
            effect_id,
            status=status,
            evidence_ref=evidence_ref,
            generation=generation,
        )

    finish_effect = complete_effect

    def reconcile_effect(
        self,
        component_id: str,
        effect_id: str,
        *,
        status: str,
        evidence_ref: str = "",
        generation: int | None = None,
    ) -> IsolationSnapshot:
        """Reconcile an in-flight or unknown effect using bounded evidence."""
        component_id = _identifier(component_id, "component id")
        effect_id = _identifier(effect_id, "effect id")
        status = _effect_status(status)
        evidence_ref = _evidence_ref(evidence_ref)
        state = self._component(component_id)
        self._check_generation(state, generation)
        current = state.effects.get(effect_id)
        if current is None:
            raise IsolationError("unknown effect")
        if current.status == status:
            if current.evidence_ref != evidence_ref:
                raise IsolationError("effect reconciliation conflicts")
            return self.snapshot(component_id)
        if current.status not in {"in_flight", "unknown"}:
            raise IsolationError("effect is already finalized")
        state.effects[effect_id] = EffectRecord(effect_id, status, evidence_ref)
        return self.snapshot(component_id)

    def reconcile(
        self,
        component_id: str,
        observations: Mapping[str, str],
        *,
        generation: int | None = None,
    ) -> IsolationSnapshot:
        """Atomically record a bounded set of effect observations."""
        if not isinstance(observations, Mapping) or not observations:
            raise IsolationError("effect observations are required")
        component_id = _identifier(component_id, "component id")
        state = self._component(component_id)
        self._check_generation(state, generation)
        normalized: list[tuple[str, str]] = []
        for effect_id, status in observations.items():
            effect_id = _identifier(effect_id, "effect id")
            status = _effect_status(status)
            current = state.effects.get(effect_id)
            if current is None:
                raise IsolationError("unknown effect")
            if current.status not in {"in_flight", "unknown"} and current.status != status:
                raise IsolationError("effect is already finalized")
            normalized.append((effect_id, status))
        for effect_id, status in normalized:
            current = state.effects[effect_id]
            state.effects[effect_id] = EffectRecord(effect_id, status, current.evidence_ref)
        return self.snapshot(component_id)

    def drain(self, component_id: str) -> IsolationSnapshot:
        """Stop new effects for one module; existing effects are untouched."""
        component_id = _identifier(component_id, "component id")
        state = self._component(component_id)
        if state.state == "running":
            state.state = "draining"
            state.generation += 1
        elif state.state not in {"draining", "quiesced", "isolated"}:
            raise IsolationError("invalid drain transition")
        return self.snapshot(component_id)

    request_drain = drain

    def quiesce(self, component_id: str) -> IsolationSnapshot:
        """Enter quiescence only after every in-flight effect is reconciled."""
        component_id = _identifier(component_id, "component id")
        state = self._component(component_id)
        if state.state == "running":
            raise IsolationError("module must be draining before quiescence")
        if state.state == "draining":
            if self.snapshot(component_id).in_flight:
                raise IsolationError("in-flight effects require reconciliation")
            state.state = "quiesced"
            state.generation += 1
        elif state.state not in {"quiesced", "isolated"}:
            raise IsolationError("invalid quiesce transition")
        return self.snapshot(component_id)

    def isolate(self, component_id: str, *, reason: str) -> IsolationSnapshot:
        """Isolate one quiesced module without affecting other components."""
        component_id = _identifier(component_id, "component id")
        reason = _reason(reason)
        state = self._component(component_id)
        if state.state == "draining":
            self.quiesce(component_id)
        if state.state == "isolated":
            if state.reason != reason:
                raise IsolationError("isolation reason conflicts")
            return self.snapshot(component_id)
        if state.state != "quiesced":
            raise IsolationError("module must be quiesced before isolation")
        state.state = "isolated"
        state.reason = reason
        state.generation += 1
        return self.snapshot(component_id)

    def resume(self, component_id: str) -> IsolationSnapshot:
        """Resume only after isolation has no unresolved effect observations."""
        component_id = _identifier(component_id, "component id")
        state = self._component(component_id)
        snapshot = self.snapshot(component_id)
        if snapshot.in_flight:
            raise IsolationError("in-flight effects require reconciliation")
        if snapshot.unresolved:
            raise IsolationError("unknown effects require resolution")
        if state.state in {"quiesced", "isolated"}:
            state.state = "running"
            state.reason = ""
            state.generation += 1
        elif state.state != "running":
            raise IsolationError("module is not resumable")
        return self.snapshot(component_id)

    def _component(self, component_id: str) -> _ComponentState:
        try:
            return self._components[component_id]
        except KeyError as exc:
            raise IsolationError("component is not registered") from exc

    @staticmethod
    def _check_generation(state: _ComponentState, generation: int | None) -> None:
        if generation is not None and (type(generation) is not int or generation != state.generation):
            raise IsolationError("stale isolation generation")


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise IsolationError(f"invalid {label}")
    return value


def _reason(value: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > MAX_REASON_LENGTH
        or any(ord(char) < 32 for char in value)
    ):
        raise IsolationError("invalid isolation reason")
    return value


def _evidence_ref(value: str) -> str:
    if value == "":
        return value
    return _identifier(value, "evidence reference")


def _effect_status(value: str) -> str:
    if value not in _FINAL_EFFECT_STATES:
        raise IsolationError("invalid effect status")
    return value


MicroModuleIsolation = IsolationController


__all__ = [
    "EffectRecord",
    "IsolationController",
    "IsolationError",
    "IsolationSnapshot",
    "MAX_COMPONENTS",
    "MAX_EFFECTS_PER_COMPONENT",
    "MicroModuleIsolation",
]
