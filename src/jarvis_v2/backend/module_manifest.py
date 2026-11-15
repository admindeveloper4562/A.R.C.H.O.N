"""Pure validation for the ATLAS module manifests.

This module deliberately does not load configuration, contact a health
endpoint, open a database, or start a process.  The policy constants mirror
the ten active entries in ``config/modules.json`` and are intentionally kept
immutable so validation cannot alter the configured module set.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping


class ManifestValidationError(ValueError):
    """Raised when a module manifest is malformed or exceeds its policy."""


MODULE_IDS = MappingProxyType(
    {
        1: "core",
        2: "sda",
        3: "backend",
        4: "runtime",
        5: "research",
        6: "tws",
        7: "wic",
        8: "finance",
        9: "guardian",
        10: "automation",
    }
)
ACTIVE_MODULE_KEYS = frozenset(MODULE_IDS.values())

# Dependencies are explicit even where a module has no dependencies.  They
# describe the existing foundation layering; Business is intentionally absent.
EXPECTED_DEPENDENCIES = MappingProxyType(
    {
        "core": (),
        "sda": ("core",),
        "backend": ("core",),
        "runtime": ("backend", "core"),
        "research": ("backend",),
        "tws": ("backend",),
        "wic": ("backend",),
        "finance": ("backend",),
        "guardian": ("backend",),
        "automation": ("backend", "core"),
    }
)

# Permission scopes are intentionally module-local.  A manifest may declare
# health/read access for itself, but cannot grant an administrative or foreign
# module scope through this contract.
ALLOWED_PERMISSION_SCOPES = MappingProxyType(
    {
        key: frozenset({f"{key}:read", f"{key}:health"})
        for key in ACTIVE_MODULE_KEYS
    }
)


@dataclass(frozen=True)
class ModuleManifest:
    """The validated, typed representation of one module manifest."""

    module_id: int
    key: str
    dependencies: tuple[str, ...]
    health_endpoint_label: str
    permission_scopes: frozenset[str]


def _fail(message: str) -> None:
    raise ManifestValidationError(message)


def _strings(
    value: Any, field: str, *, unique: bool = True, allow_empty: bool = False
) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple, set, frozenset)):
        _fail(f"{field} must be a collection of strings")
    values = tuple(value)
    if not allow_empty and not values:
        _fail(f"{field} must not be empty")
    if any(type(item) is not str or not item for item in values):
        _fail(f"{field} must contain non-empty strings")
    if unique and len(values) != len(set(values)):
        _fail(f"{field} must not contain duplicates")
    return values


def validate_module_manifest(manifest: ModuleManifest | Mapping[str, Any]) -> ModuleManifest:
    """Validate one manifest without performing any external side effects."""

    if isinstance(manifest, ModuleManifest):
        candidate = manifest
    elif isinstance(manifest, Mapping):
        required = {
            "module_id",
            "key",
            "dependencies",
            "health_endpoint_label",
            "permission_scopes",
        }
        if set(manifest) != required:
            _fail("manifest must contain exactly the typed manifest fields")
        module_id = manifest["module_id"]
        key = manifest["key"]
        if type(module_id) is not int or module_id not in MODULE_IDS:
            _fail("module_id is not a stable active module ID")
        if type(key) is not str or MODULE_IDS[module_id] != key:
            _fail("module_id and key do not identify the same active module")
        if type(manifest["health_endpoint_label"]) is not str:
            _fail("health_endpoint_label must be a string")
        candidate = ModuleManifest(
            module_id=module_id,
            key=key,
            dependencies=_strings(
                manifest["dependencies"], "dependencies", allow_empty=True
            ),
            health_endpoint_label=manifest["health_endpoint_label"],
            permission_scopes=frozenset(
                _strings(manifest["permission_scopes"], "permission_scopes")
            ),
        )
    else:
        _fail("manifest must be a ModuleManifest or mapping")

    if (
        type(candidate.module_id) is not int
        or type(candidate.key) is not str
        or not isinstance(candidate.dependencies, tuple)
        or not isinstance(candidate.permission_scopes, frozenset)
        or type(candidate.health_endpoint_label) is not str
    ):
        _fail("manifest fields have invalid types")
    if MODULE_IDS.get(candidate.module_id) != candidate.key:
        _fail("module_id and key do not identify the same active module")
    if candidate.key not in ACTIVE_MODULE_KEYS or candidate.key == "business":
        _fail("unknown or suspended module")
    if candidate.dependencies != EXPECTED_DEPENDENCIES[candidate.key]:
        _fail("dependencies do not match the explicit module contract")
    if any(type(item) is not str or not item for item in candidate.dependencies):
        _fail("dependencies must contain non-empty strings")
    if any(type(item) is not str or not item for item in candidate.permission_scopes):
        _fail("permission_scopes must contain non-empty strings")
    if not candidate.permission_scopes:
        _fail("permission_scopes must not be empty")
    if candidate.health_endpoint_label != candidate.key:
        _fail("health endpoint label must equal the stable module key")
    if not candidate.permission_scopes <= ALLOWED_PERMISSION_SCOPES[candidate.key]:
        _fail("permission scope exceeds the module contract")
    return candidate


def validate_module_manifests(
    manifests: list[Any] | tuple[Any, ...],
) -> tuple[ModuleManifest, ...]:
    """Validate the complete active set and return it in stable ID order."""

    if not isinstance(manifests, (list, tuple)):
        _fail("manifests must be an ordered collection")
    if len(manifests) != len(MODULE_IDS):
        _fail("exactly ten active module manifests are required")
    validated = tuple(validate_module_manifest(item) for item in manifests)
    ids = tuple(item.module_id for item in validated)
    if set(ids) != set(MODULE_IDS) or len(ids) != len(set(ids)):
        _fail("manifests must contain each stable module ID exactly once")
    if any(item.key == "business" for item in validated):
        _fail("Business is not an active module")
    return tuple(sorted(validated, key=lambda item: item.module_id))


__all__ = [
    "ACTIVE_MODULE_KEYS",
    "ALLOWED_PERMISSION_SCOPES",
    "EXPECTED_DEPENDENCIES",
    "MODULE_IDS",
    "ManifestValidationError",
    "ModuleManifest",
    "validate_module_manifest",
    "validate_module_manifests",
]
