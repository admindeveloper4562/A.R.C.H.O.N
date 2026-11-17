import unittest

from jarvis_v2.finance.mira_connector import (
    MIRA_READ_SCOPE,
    MiraConnectorTokenBroker,
)


class MiraConnectorTokenTests(unittest.TestCase):
    def test_issue_is_short_lived_scoped_and_identity_bound(self):
        broker = MiraConnectorTokenBroker()
        token = broker.issue("archon-finance", token_id="mira-token-1", ttl_seconds=60)
        self.assertEqual(token.scope, MIRA_READ_SCOPE)
        self.assertTrue(broker.authorize("archon-finance", token.token_id))
        self.assertFalse(broker.authorize("other-service", token.token_id))
        self.assertFalse(broker.authorize("archon-finance", token.token_id, "mira:write"))
        self.assertLessEqual(token.expires_at, __import__("time").time() + 61)

    def test_revoke_is_immediate_and_audit_is_redacted(self):
        broker = MiraConnectorTokenBroker()
        token = broker.issue("archon-finance", token_id="mira-token-2")
        broker.revoke(token.token_id)
        self.assertFalse(broker.authorize("archon-finance", token.token_id))
        audit = broker.audit()[0]
        self.assertEqual(audit["connector"], "mira")
        self.assertEqual(audit["scopes"], frozenset({MIRA_READ_SCOPE}))
        self.assertTrue(audit["revoked"])
        self.assertNotIn("credential_ref", audit)
        self.assertNotIn("admin", repr(audit).lower())

    def test_token_registration_is_idempotent_but_conflicts_fail(self):
        broker = MiraConnectorTokenBroker()
        first = broker.issue("archon-finance", token_id="mira-token-3")
        self.assertEqual(broker.issue("archon-finance", token_id="mira-token-3"), first)
        with self.assertRaisesRegex(ValueError, "grant registration conflict"):
            broker.issue("other-service", token_id="mira-token-3")

    def test_ttl_is_bounded_by_the_shared_connector_policy(self):
        broker = MiraConnectorTokenBroker()
        with self.assertRaisesRegex(ValueError, "TTL"):
            broker.issue("archon-finance", ttl_seconds=3601)


if __name__ == "__main__":
    unittest.main()
