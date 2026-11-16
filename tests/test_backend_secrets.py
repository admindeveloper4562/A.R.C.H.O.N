import json
import unittest

from jarvis_v2.backend import SecretBoundaryError, SecretStore, SecretUnavailable


class BackendSecretTests(unittest.TestCase):
    def test_allowlisted_value_is_redacted_outside_explicit_use(self):
        raw = "opaque-value-123456"
        store = SecretStore({"ARCHON_TEST_VALUE": raw, "OTHER_VALUE": "ignored"}, allowlist=["ARCHON_TEST_VALUE"])
        value = store.get("ARCHON_TEST_VALUE")
        self.assertEqual(value.reveal(), raw)
        self.assertNotIn(raw, str(value))
        self.assertNotIn(raw, repr(value))
        self.assertNotIn(raw, store.redact(f"event={raw}"))

    def test_metadata_is_safe_for_external_telemetry(self):
        raw = "opaque-value-abcdef"
        store = SecretStore({"ARCHON_TEST_VALUE": raw}, allowlist=["ARCHON_TEST_VALUE"])
        metadata = store.public_metadata("ARCHON_TEST_VALUE")
        self.assertNotIn(raw, json.dumps(metadata))
        self.assertEqual(metadata["length"], len(raw.encode()))
        self.assertEqual(metadata["sha256"], store.get("ARCHON_TEST_VALUE").digest)

    def test_unallowlisted_and_missing_values_fail_closed(self):
        store = SecretStore({"ARCHON_TEST_VALUE": "opaque-value-123456"}, allowlist=["ARCHON_TEST_VALUE", "MISSING_VALUE"])
        with self.assertRaises(SecretUnavailable):
            store.get("OTHER_VALUE")
        with self.assertRaises(SecretUnavailable):
            store.get("MISSING_VALUE")

    def test_names_values_and_allowlist_are_bounded(self):
        with self.assertRaises(SecretBoundaryError):
            SecretStore({"ARCHON_TEST_VALUE": "value"}, allowlist=[])
        with self.assertRaises(SecretBoundaryError):
            SecretStore({"archon_test_value": "value"}, allowlist=["archon_test_value"])
        with self.assertRaises(SecretBoundaryError):
            SecretStore({"ARCHON_TEST_VALUE": ""}, allowlist=["ARCHON_TEST_VALUE"])
        with self.assertRaises(SecretBoundaryError):
            SecretStore({"ARCHON_TEST_VALUE": "x" * (64 * 1024 + 1)}, allowlist=["ARCHON_TEST_VALUE"])


if __name__ == "__main__":
    unittest.main()
