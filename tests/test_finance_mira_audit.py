import unittest

from jarvis_v2.finance.mira_audit import (
    MiraAuditSnapshot,
    authorize_mira_method,
    schema_sha256,
)


class MiraAuditTests(unittest.TestCase):
    def snapshot(self):
        schema = {
            "couple_accounts": "CREATE TABLE couple_accounts(id TEXT PRIMARY KEY)",
            "couple_account_entries": "CREATE TABLE couple_account_entries(id TEXT PRIMARY KEY)",
            "couple_account_links": "CREATE TABLE couple_account_links(id TEXT PRIMARY KEY)",
            "couple_budgets": "CREATE TABLE couple_budgets(id TEXT PRIMARY KEY)",
            "couple_categories": "CREATE TABLE couple_categories(id TEXT PRIMARY KEY)",
            "couple_login_attempts": "CREATE TABLE couple_login_attempts(id TEXT PRIMARY KEY)",
            "couple_sessions": "CREATE TABLE couple_sessions(id TEXT PRIMARY KEY)",
            "couple_settings": "CREATE TABLE couple_settings(id TEXT PRIMARY KEY)",
            "couple_transactions": "CREATE TABLE couple_transactions(id TEXT PRIMARY KEY)",
        }
        return MiraAuditSnapshot(
            worker_name="personal-management",
            worker_version_id="1f2dc83a-d844-4f39-bdda-e59300cb56e8",
            worker_source_sha256="7" * 64,
            d1_name="mira-finance",
            d1_uuid="140fc8c8-c995-4cb7-b7d6-0649dc157e29",
            d1_schema_sha256=schema_sha256(schema),
            d1_tables=tuple(schema),
            db_binding_name="DB",
            db_binding_uuid="140fc8c8-c995-4cb7-b7d6-0649dc157e29",
            secret_binding_names=("ADMIN_PASSWORD_HASH", "ADMIN_PIN"),
            session_cookie_name="__Host-mira_couple",
            session_ttl_seconds=7 * 24 * 60 * 60,
            same_origin_enforced=True,
            partner_scope_enforced=True,
            read_route_count=8,
            write_route_count=12,
        )

    def test_valid_snapshot_is_bounded_and_read_only(self):
        evidence = self.snapshot().evidence()
        self.assertEqual(evidence["data_access"], "metadata_only; no financial rows read")
        self.assertTrue(evidence["authorization"]["archon_read_only_policy"])

    def test_worker_write_capability_does_not_expand_archon_scope(self):
        self.assertTrue(authorize_mira_method("GET"))
        for method in ("POST", "PUT", "PATCH", "DELETE"):
            self.assertFalse(authorize_mira_method(method))

    def test_binding_and_auth_boundary_mismatch_is_rejected(self):
        snapshot = self.snapshot()
        invalid = snapshot.__class__(**{**snapshot.__dict__, "db_binding_uuid": "0" * 36})
        with self.assertRaisesRegex(ValueError, "binding mismatch"):
            invalid.validate()

    def test_secret_values_are_not_part_of_evidence(self):
        evidence = self.snapshot().evidence()
        self.assertNotIn("123456", str(evidence))
        self.assertNotIn("plaintext-secret", str(evidence))
        self.assertEqual(evidence["authorization"]["secret_binding_names"], [
            "ADMIN_PASSWORD_HASH", "ADMIN_PIN",
        ])


if __name__ == "__main__":
    unittest.main()
