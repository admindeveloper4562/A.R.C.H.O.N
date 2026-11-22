import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DevelopmentDelegationDraftTests(unittest.TestCase):
    def test_policy_is_scoped_to_archon_and_inactive_without_signed_receipt(self):
        policy = json.loads((ROOT / "config/autonomy-policy.json").read_text())
        self.assertEqual(policy["schema"], "archon.autonomy-policy/v1")
        self.assertEqual(policy["repository"]["owner"], "admindeveloper4562")
        self.assertEqual(policy["repository"]["name"], "A.R.C.H.O.N")
        self.assertFalse(policy["activation"]["enabled"])
        self.assertTrue(policy["activation"]["requires_owner_signed_receipt_bound_to_policy_sha256"])
        self.assertIsNone(policy["activation"]["signature"])
        self.assertIsNone(policy["activation"]["owner_receipt_id"])

    def test_policy_keeps_protected_and_external_effects_denied(self):
        policy = json.loads((ROOT / "config/autonomy-policy.json").read_text())
        denied = set(policy["operations"]["denied"])
        self.assertIn("write_main_or_rewrite_history", denied)
        self.assertIn("change_trust_roots_or_signing_identities", denied)
        self.assertIn("perform_financial_transactions", denied)
        self.assertIn("send_external_communications", denied)
        self.assertEqual(policy["network"]["default"], "deny")
        self.assertFalse(policy["stop_and_revocation"]["agent_may_clear_stop"])
        self.assertTrue(policy["quality_gates"]["only_serialized_merger_may_update_develop"])
        self.assertTrue(policy["quality_gates"]["merger_must_differ_from_author_and_qc"])
        self.assertIn("develop_updates_only_by_serialized_merger", policy["resources"]["github_repository_writes"])


if __name__ == "__main__":
    unittest.main()
