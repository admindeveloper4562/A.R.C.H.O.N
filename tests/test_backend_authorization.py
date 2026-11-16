import time
import unittest
from pathlib import Path

from jarvis_v2.backend import AuthorizationError, AuthorizationServer, OwnerApproval
from jarvis_v2.core import ModuleRegistry


ROOT = Path(__file__).resolve().parents[1]


class BackendAuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.registry = ModuleRegistry.from_config(ROOT / "config/modules.json")
        self.server = AuthorizationServer(self.registry)

    def test_each_module_can_only_use_its_own_read_and_health_grant(self):
        for capability in self.registry.all():
            identity_id = f"{capability.key}-service"
            self.server.register_identity(identity_id, capability.key)
            grant = self.server.grant(identity_id, capability.key, [f"{capability.key}:read", f"{capability.key}:health"])
            self.assertTrue(self.server.authorize(identity_id, capability.key, f"{capability.key}:read"))
            self.assertTrue(self.server.authorize(identity_id, capability.key, f"{capability.key}:health"))
            self.assertEqual(self.server.require(identity_id, capability.key, f"{capability.key}:read"), grant)
            self.assertFalse(self.server.authorize(identity_id, capability.key, f"{capability.key}:write"))
            self.assertFalse(self.server.authorize(identity_id, capability.key, "*"))
            for foreign in self.registry.all():
                if foreign.key != capability.key:
                    self.assertFalse(self.server.authorize(identity_id, foreign.key, f"{foreign.key}:read"))

    def test_cross_module_grant_requires_exact_owner_approval(self):
        self.server.register_identity("core-service", "core")
        with self.assertRaises(AuthorizationError):
            self.server.grant("core-service", "backend", ["backend:read"])
        approval = OwnerApproval.for_grant("owner-approval-1", "core-service", "backend", ["backend:read"])
        grant = self.server.grant("core-service", "backend", ["backend:read"], approval=approval)
        self.assertTrue(self.server.authorize("core-service", "backend", "backend:read", grant_id=grant.grant_id))
        self.assertFalse(self.server.authorize("core-service", "backend", "backend:health", grant_id=grant.grant_id))

    def test_approval_and_identity_conflicts_fail_closed(self):
        self.server.register_identity("core-service", "core")
        approval = OwnerApproval.for_grant("owner-approval-2", "core-service", "backend", ["backend:read"])
        with self.assertRaises(AuthorizationError):
            self.server.grant("core-service", "backend", ["backend:health"], approval=approval)
        with self.assertRaises(AuthorizationError):
            self.server.register_identity("core-service", "guardian")
        self.assertFalse(self.server.authorize("unknown", "core", "core:read"))

    def test_revoke_and_expiry_remove_access(self):
        self.server.register_identity("backend-service", "backend")
        grant = self.server.grant("backend-service", "backend", ["backend:read"], ttl_seconds=1)
        self.assertTrue(self.server.authorize("backend-service", "backend", "backend:read"))
        self.server.revoke(grant.grant_id)
        self.assertFalse(self.server.authorize("backend-service", "backend", "backend:read"))
        short = self.server.grant("backend-service", "backend", ["backend:health"], ttl_seconds=1)
        self.assertGreater(short.expires_at, time.time())


if __name__ == "__main__":
    unittest.main()
