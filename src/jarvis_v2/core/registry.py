"""Typed, immutable Core module capability registry."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from jarvis_v2.backend.module_manifest import (
    EXPECTED_DEPENDENCIES,
    MODULE_IDS,
    ManifestValidationError,
    validate_module_manifests,
)


class CoreRegistryError(ValueError):
    """Raised when the Core boundary receives an invalid module request."""


@dataclass(frozen=True)
class ModuleCapability:
    """The immutable capability view exposed by Core."""

    module_id: int
    key: str
    dependencies: tuple[str, ...]
    permission_scopes: frozenset[str]


class ModuleRegistry:
    """Resolve stable module identities without mutable global state."""

    def __init__(self, capabilities: tuple[ModuleCapability, ...]) -> None:
        self._by_id = MappingProxyType({item.module_id: item for item in capabilities})
        self._by_key = MappingProxyType({item.key: item for item in capabilities})

    @classmethod
    def from_manifests(cls, manifests: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...]) -> "ModuleRegistry":
        try:
            validated = validate_module_manifests(list(manifests))
        except (ManifestValidationError, TypeError) as exc:
            raise CoreRegistryError(str(exc)) from exc
        return cls(
            tuple(
                ModuleCapability(
                    module_id=item.module_id,
                    key=item.key,
                    dependencies=item.dependencies,
                    permission_scopes=item.permission_scopes,
                )
                for item in validated
            )
        )

    @classmethod
    def from_config(cls, path: str | Path) -> "ModuleRegistry":
        """Load the repository module list and apply the shared scope contract."""
        config_path = Path(path)
        try:
            payload = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CoreRegistryError("module configuration is unreadable") from exc
        if not isinstance(payload, dict) or payload.get("schema") != "jarvis-v2.modules/1":
            raise CoreRegistryError("unsupported module configuration")
        if payload.get("business_module_enabled") is not False:
            raise CoreRegistryError("Business must remain excluded")
        entries = payload.get("modules")
        if not isinstance(entries, list):
            raise CoreRegistryError("module configuration must contain a list")
        manifests = []
        for entry in entries:
            if not isinstance(entry, dict):
                raise CoreRegistryError("module entry must be an object")
            module_id = entry.get("id")
            key = entry.get("key")
            if type(module_id) is not int or MODULE_IDS.get(module_id) != key:
                raise CoreRegistryError("module ID and key are not a stable pair")
            manifests.append(
                {
                    "module_id": module_id,
                    "key": key,
                    "dependencies": list(EXPECTED_DEPENDENCIES[key]),
                    "health_endpoint_label": key,
                    "permission_scopes": [f"{key}:read", f"{key}:health"],
                }
            )
        return cls.from_manifests(manifests)

    def all(self) -> tuple[ModuleCapability, ...]:
        """Return capabilities in immutable module-ID order."""
        return tuple(self._by_id[module_id] for module_id in MODULE_IDS)

    def resolve(self, module: int | str) -> ModuleCapability:
        if type(module) is int:
            capability = self._by_id.get(module)
        elif type(module) is str:
            capability = self._by_key.get(module)
        else:
            raise CoreRegistryError("module identity must be an integer ID or key")
        if capability is None:
            raise CoreRegistryError("unknown module identity")
        return capability

    def authorize(self, module: int | str, scope: str) -> bool:
        if type(scope) is not str or not scope:
            raise CoreRegistryError("authorization scope must be a non-empty string")
        return scope in self.resolve(module).permission_scopes

    @property
    def by_id(self) -> Mapping[int, ModuleCapability]:
        return self._by_id


@dataclass(frozen=True)
class CoreService:
    """Small Core boundary that exposes only registry-backed operations."""

    registry: ModuleRegistry

    @classmethod
    def from_config(cls, path: str | Path) -> "CoreService":
        return cls(ModuleRegistry.from_config(path))

    def module(self, identity: int | str) -> ModuleCapability:
        return self.registry.resolve(identity)

    def can(self, identity: int | str, scope: str) -> bool:
        return self.registry.authorize(identity, scope)


__all__ = ["CoreRegistryError", "CoreService", "ModuleCapability", "ModuleRegistry"]
