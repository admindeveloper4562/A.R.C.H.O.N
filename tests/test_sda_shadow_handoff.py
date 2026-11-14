import unittest

from jarvis_v2.sda.handoff import EVIDENCE_KEYS, HandoffEvidence


class ShadowHandoffTests(unittest.TestCase):
    def test_missing_prerequisites_have_stable_keys(self):
        report = HandoffEvidence().report()

        self.assertEqual(report["missing"], list(EVIDENCE_KEYS))
        self.assertEqual(report["missing_evidence_keys"], list(EVIDENCE_KEYS))
        self.assertEqual(set(report["evidence"]), set(EVIDENCE_KEYS))

    def test_owner_approval_is_required_for_readiness(self):
        evidence = dict.fromkeys(EVIDENCE_KEYS, True)
        evidence["owner_approved"] = False

        report = HandoffEvidence(**evidence).report()

        self.assertFalse(report["ready_for_controlled_cutover"])
        self.assertEqual(report["missing_evidence_keys"], ["owner_approved"])
        self.assertTrue(report["owner_approval_required"])

    def test_shadow_mode_cannot_claim_or_promote(self):
        report = HandoffEvidence(*([True] * len(EVIDENCE_KEYS))).report()

        self.assertTrue(report["shadow_mode"])
        self.assertFalse(report["claims_live_task_ownership"])
        self.assertFalse(report["self_promoted"])
        self.assertFalse(report["actual_cutover_performed"])


if __name__ == "__main__":
    unittest.main()
