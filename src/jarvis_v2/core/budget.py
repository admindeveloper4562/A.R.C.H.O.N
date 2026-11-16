"""Bounded Core resource admission backed by Guardian slot priority."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from types import MappingProxyType

from jarvis_v2.guardian.priority import SlotPriority


class ResourceBudgetError(ValueError):
    """Raised when a resource budget request is invalid or loses its fence."""


class ResourceBudget:
    """Enforce global capacity, per-device limits and Guardian priority."""

    def __init__(
        self,
        capacity: int,
        *,
        device_limits: Mapping[str, int] | None = None,
        slots: Iterable[str] | None = None,
    ) -> None:
        if type(capacity) is not int or capacity < 1:
            raise ResourceBudgetError("capacity must be a positive integer")
        configured_slots = tuple(slots) if slots is not None else tuple(
            f"slot-{index}" for index in range(capacity)
        )
        if len(configured_slots) != capacity:
            raise ResourceBudgetError("slot count must equal capacity")
        if device_limits is None:
            device_limits = {}
        if not isinstance(device_limits, Mapping):
            raise ResourceBudgetError("device limits must be a mapping")
        normalized_limits: dict[str, int] = {}
        for device, limit in device_limits.items():
            if not isinstance(device, str) or not device or type(limit) is not int or limit < 0:
                raise ResourceBudgetError("device limits must contain non-negative integers")
            normalized_limits[device] = limit
        self._priority = SlotPriority(configured_slots)
        self._device_limits = MappingProxyType(normalized_limits)
        self._holders: dict[str, tuple[str, str, str]] = {}

    @property
    def capacity(self) -> int:
        return len(self._priority.slots)

    @property
    def slots(self) -> tuple[str, ...]:
        return self._priority.slots

    @property
    def available_slots(self) -> tuple[str, ...]:
        return self._priority.available_slots

    @property
    def guardian_pending(self) -> bool:
        return self._priority.guardian_pending

    @property
    def device_limits(self) -> Mapping[str, int]:
        return self._device_limits

    @property
    def held_slots(self) -> dict[str, dict[str, str]]:
        return {
            slot: {"owner": owner, "device": device}
            for slot, (owner, device, _) in self._holders.items()
        }

    @property
    def device_usage(self) -> dict[str, int]:
        usage: dict[str, int] = {}
        for _, device, _ in self._holders.values():
            usage[device] = usage.get(device, 0) + 1
        return usage

    def guardian_request(self, compatible_slots: Iterable[str] | None = None) -> None:
        self._priority.guardian_request(compatible_slots)

    def claim(
        self,
        owner: str,
        *,
        device: str = "default",
        compatible_slots: Iterable[str] | None = None,
        guardian: bool = False,
    ) -> str | None:
        self._validate_owner(owner)
        self._validate_device(device)
        if owner == "guardian" and not guardian:
            raise ResourceBudgetError("guardian owner requires guardian claim")
        if self.device_usage.get(device, 0) >= self._device_limits.get(device, self.capacity):
            return None
        requester = "guardian" if guardian else owner
        slot = self._priority.claim(requester, compatible_slots)
        if slot is None:
            return None
        self._holders[slot] = (owner, device, requester)
        return slot

    def finish(self, owner: str, slot: str, *, device: str | None = None) -> None:
        self._validate_owner(owner)
        if not isinstance(slot, str) or slot not in self._holders:
            raise ResourceBudgetError("slot is not held")
        held_owner, held_device, requester = self._holders[slot]
        if held_owner != owner or (device is not None and device != held_device):
            raise ResourceBudgetError("slot ownership mismatch")
        self._priority.finish(requester, slot)
        del self._holders[slot]

    @staticmethod
    def _validate_owner(owner: str) -> None:
        if not isinstance(owner, str) or not owner:
            raise ResourceBudgetError("owner is required")

    @staticmethod
    def _validate_device(device: str) -> None:
        if not isinstance(device, str) or not device:
            raise ResourceBudgetError("device is required")


__all__ = ["ResourceBudget", "ResourceBudgetError"]
