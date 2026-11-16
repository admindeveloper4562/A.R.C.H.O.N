import unittest

from jarvis_v2.guardian.fencing import WriterFence, WriterFenceError


class GuardianFencingTests(unittest.TestCase):
    def setUp(self):
        self.now = 100.0
        self.fence = WriterFence(clock=lambda: self.now)

    def test_only_one_writer_and_stale_lease_is_rejected_after_handoff(self):
        first = self.fence.acquire("writer-a", ttl_seconds=10)
        with self.assertRaisesRegex(WriterFenceError, "already leased"):
            self.fence.acquire("writer-b")

        second = self.fence.handoff(first, "writer-b", ttl_seconds=10)
        self.assertEqual(self.fence.snapshot()["owner_id"], "writer-b")
        with self.assertRaisesRegex(WriterFenceError, "stale"):
            self.fence.assert_current(first)
        self.fence.assert_current(second)

    def test_expiry_allows_new_generation_but_old_lease_cannot_return(self):
        first = self.fence.acquire("writer-a", ttl_seconds=5)
        self.now = 105.0
        second = self.fence.acquire("writer-b", ttl_seconds=5)
        self.assertGreater(second.generation, first.generation)
        with self.assertRaisesRegex(WriterFenceError, "stale"):
            self.fence.release(first)

    def test_renew_and_release_require_current_lease(self):
        lease = self.fence.acquire("writer-a", ttl_seconds=5)
        renewed = self.fence.renew(lease, ttl_seconds=20)
        self.assertEqual(renewed.lease_id, lease.lease_id)
        self.fence.release(renewed)
        self.assertIsNone(self.fence.snapshot()["owner_id"])
        with self.assertRaisesRegex(WriterFenceError, "stale"):
            self.fence.release(renewed)

    def test_invalid_ttl_and_owner_fail_closed(self):
        with self.assertRaises(WriterFenceError):
            self.fence.acquire("writer a")
        with self.assertRaises(WriterFenceError):
            self.fence.acquire("writer-a", ttl_seconds=0)


if __name__ == "__main__":
    unittest.main()
