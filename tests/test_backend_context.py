import unittest

from jarvis_v2.backend import ContextPackError, ContextPacker, estimate_tokens


class BackendContextTests(unittest.TestCase):
    def test_protected_sections_survive_history_reduction(self):
        packer = ContextPacker(default_max_tokens=160)
        requirements = {"task_id": "BACK-009", "acceptance": ["keep exact requirements"]}
        policy = {"stop": True, "rules": ["default deny", "preserve receipts"]}
        receipts = [{"candidate_sha": "abc", "status": "passed"}]
        packet = packer.pack(
            requirements,
            policy,
            receipts,
            history=[{"step": index, "detail": "optional" * 20} for index in range(8)],
        )
        self.assertEqual(packet["requirements"], requirements)
        self.assertEqual(packet["policy"], policy)
        self.assertEqual(packet["recent_receipts"], receipts)
        self.assertGreater(packet["metadata"]["history_items_dropped"], 0)
        self.assertEqual(packet["history"][-1]["step"], 7)

    def test_protected_content_fails_closed_when_budget_is_too_small(self):
        with self.assertRaises(ContextPackError):
            ContextPacker().pack({"acceptance": "x" * 500}, {"stop": True}, [], max_tokens=2)

    def test_packet_digest_is_deterministic_and_empty_history_is_valid(self):
        arguments = ({"task": "BACK-009"}, {"stop": True}, [{"id": "r1"}], [])
        first = ContextPacker().pack(*arguments)
        second = ContextPacker().pack(*arguments)
        self.assertEqual(first["metadata"]["protected_sha256"], second["metadata"]["protected_sha256"])
        self.assertEqual(first["history"], [])
        self.assertGreaterEqual(estimate_tokens("x"), 1)

    def test_restricted_fields_and_invalid_budgets_are_rejected(self):
        with self.assertRaises(ContextPackError):
            ContextPacker().pack({"raw_prompt": "do not retain"}, {}, [])
        with self.assertRaises(ContextPackError):
            ContextPacker(default_max_tokens=0)
        with self.assertRaises(ContextPackError):
            ContextPacker().pack({}, {}, recent_receipts="not-a-list")


if __name__ == "__main__":
    unittest.main()
