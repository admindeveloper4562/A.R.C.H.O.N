import tempfile
import unittest
from pathlib import Path

from jarvis_v2.backend.authorization import AuthorizationServer
from jarvis_v2.backend.event_bus import EventBus
from jarvis_v2.core.dispatch import DispatchStore
from jarvis_v2.core.registry import ModuleRegistry
from jarvis_v2.runtime import RuntimeSecurity, RuntimeService


ROOT = Path(__file__).parents[1]


class RuntimeSecurityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        path = Path(self.temp.name) / "runtime.sqlite"
        registry = ModuleRegistry.from_config(ROOT / "config/modules.json")
        authorization = AuthorizationServer(registry)
        self.owner = authorization.register_identity("owner", "runtime", kind="operator")
        self.other = authorization.register_identity("other", "runtime", kind="operator")
        for identity_id, grant_id in (("owner", "owner-grant"), ("other", "other-grant")):
            authorization.grant(
                identity_id, "runtime", ("runtime:read", "runtime:health"), grant_id=grant_id
            )
        self.service = RuntimeService(
            registry,
            authorization,
            DispatchStore(path),
            EventBus(path),
            security=RuntimeSecurity(expected_host="127.0.0.1:8765"),
        )
        self.session = self.service.issue_owner_session("owner")

    def tearDown(self):
        self.service.close()
        self.temp.cleanup()

    def request(self, path="/events", *, identity_id="owner", method="GET", **extra):
        return {
            "method": method,
            "path": path,
            "identity_id": identity_id,
            "scope": "runtime:read",
            "session_id": self.session["session_id"],
            "host": "127.0.0.1:8765",
            **extra,
        }

    def test_owner_session_requires_matching_identity_and_csrf_for_mutations(self):
        valid = self.request(
            "/tasks",
            method="POST",
            origin="http://127.0.0.1:8765",
            csrf_token=self.session["csrf_token"],
            body={
                "task_id": "secure-task",
                "target_module": "core",
                "scope": "core:read",
                "acceptance": "accepted",
                "correlation_id": "secure-correlation",
            },
        )
        self.assertEqual(self.service.handle(valid).status, 201)
        self.assertEqual(self.service.handle(dict(valid, csrf_token="wrong")).status, 403)
        self.assertEqual(self.service.handle(dict(valid, origin="http://evil.test")).status, 403)
        self.assertEqual(self.service.handle(dict(valid, identity_id="other")).status, 403)

    def test_host_origin_and_malformed_values_fail_closed(self):
        self.assertEqual(self.service.handle(self.request(host="evil.test")).status, 403)
        self.assertEqual(self.service.handle(self.request(host="bad host")).status, 400)
        self.assertEqual(
            self.service.handle(self.request(origin="http://127.0.0.1:8765/unsafe")).status,
            400,
        )
        self.assertEqual(
            self.service.handle(self.request("/tasks", method="POST", csrf_token=self.session["csrf_token"], body={})).status,
            403,
        )

    def test_rotation_invalidates_old_session_and_responses_are_hardened(self):
        request = self.request(
            "/session/rotate",
            method="POST",
            origin="http://127.0.0.1:8765",
            csrf_token=self.session["csrf_token"],
        )
        rotated = self.service.rotate_owner_session(request)
        self.assertNotEqual(rotated["session_id"], self.session["session_id"])
        self.assertEqual(
            self.service.handle(self.request(csrf_token=self.session["csrf_token"])).status,
            401,
        )
        headers = self.service.handle({"method": "GET", "path": "/events", "identity_id": "owner", "scope": "runtime:read"}).headers
        self.assertEqual(headers["X-Frame-Options"], "DENY")
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
        self.assertNotIn("Access-Control-Allow-Origin", headers)


if __name__ == "__main__":
    unittest.main()
