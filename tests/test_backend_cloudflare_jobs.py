import json
import unittest
from urllib.parse import urlsplit

from jarvis_v2.backend import CloudflareJobAdapter, CloudflareJobAdapterError
from jarvis_v2.backend.windows_agent import LocalAgentJob


class CloudflareJobAdapterTests(unittest.TestCase):
    def setUp(self):
        self.token = "job-secret-that-must-not-leak"
        self.requests = []

        def transport(request):
            self.requests.append(request)
            path = urlsplit(request.full_url).path
            body = json.loads(request.data)
            record = {
                "job_id": body.get("job_id", "job-1"),
                "idempotency_key": body.get("idempotency_key", "key-1"),
                "operation": body.get("operation", "resume_run"),
                "input_sha256": body.get("input_sha256", "a" * 64),
                "required_scope": body.get("required_scope", "public_metadata"),
                "deadline_at": body.get("deadline_at", 2_000_000_000),
                "state": "pending" if path == "/api/jobs" else "leased" if path.endswith("/claim") else "completed",
                "device_id": body.get("device_id", ""),
                "lease_id": body.get("lease_id", ""),
                "lease_expires_at": 2_000_000_060 if path.endswith("/claim") else 0,
                "result_sha256": body.get("result_sha256", ""),
                "ok": body.get("ok"),
            }
            return 201, json.dumps({"job": record}).encode()

        self.adapter = CloudflareJobAdapter(
            "https://astra-one-monitor.example.workers.dev",
            lambda: self.token,
            transport=transport,
        )

    def test_create_claim_complete_uses_durable_metadata_and_https_only(self):
        job = LocalAgentJob("job-1", "key-1", "index", "a" * 64, "public_metadata", 2_000_000_000)
        created = self.adapter.create(job)
        claimed = self.adapter.claim(created.job_id, "linux", "lease-1")
        completed = self.adapter.complete(claimed.job_id, claimed.lease_id, ok=True, result_sha256="b" * 64)
        self.assertEqual((created.state, claimed.state, completed.state), ("pending", "leased", "completed"))
        self.assertEqual(claimed.lease_id, "lease-1")
        self.assertTrue(all(urlsplit(request.full_url).scheme == "https" for request in self.requests))
        for request in self.requests:
            self.assertEqual(request.headers["Authorization"], f"Bearer {self.token}")
            self.assertNotIn(self.token.encode(), request.data)

    def test_invalid_url_and_token_fail_closed_without_network(self):
        with self.assertRaises(CloudflareJobAdapterError):
            CloudflareJobAdapter("http://monitor.example", lambda: self.token)
        adapter = CloudflareJobAdapter("https://monitor.example", lambda: "")
        job = LocalAgentJob("job-1", "key-1", "index", "a" * 64, "public_metadata", 2_000_000_000)
        with self.assertRaisesRegex(CloudflareJobAdapterError, "token"):
            adapter.create(job)

    def test_response_and_transport_failures_do_not_expose_secret(self):
        def failure(request):
            raise OSError("network failed")

        adapter = CloudflareJobAdapter("https://monitor.example", lambda: self.token, transport=failure)
        job = LocalAgentJob("job-1", "key-1", "index", "a" * 64, "public_metadata", 2_000_000_000)
        with self.assertRaisesRegex(CloudflareJobAdapterError, "request failed") as caught:
            adapter.create(job)
        self.assertNotIn(self.token, str(caught.exception))


if __name__ == "__main__":
    unittest.main()
