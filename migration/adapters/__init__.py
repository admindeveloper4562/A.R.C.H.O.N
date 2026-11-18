"""Read-only migration compatibility boundaries."""

from .legacy_contracts import LegacyContractAdapter, MigrationCompatibilityError

__all__ = ["LegacyContractAdapter", "MigrationCompatibilityError"]
