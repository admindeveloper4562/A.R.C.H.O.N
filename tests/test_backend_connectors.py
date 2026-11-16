import unittest

from jarvis_v2.backend import (
    CONNECTORS,
    ConnectorAuthorizationError,
    ConnectorBroker,
)


class BackendConnectorTests(unittest.TestCase):
    def test_each_connector_is_independently_revocable(self):
        broker = ConnectorBroker()
        grants = {
            connector: broker.grant(
                "owner-service", connector, [f"{connector}:read"], credential_ref=f"{connector}-ref"
            )
            for connector in CONNECTORS
        }
        for connector in CONNECTORS:
            self.assertTrue(broker.authorize("owner-service", connector, f"{connector}:read"))
        broker.revoke(grants["google"].grant_id)
        self.assertFalse(broker.authorize("owner-service", "google", "google:read"))
        for connector in CONNECTORS - {"google"}:
            self.assertTrue(broker.authorize("owner-service", connector, f"{connector}:read"))
        self.assertNotIn("owner-service", repr(broker.grants()[0].get("credential_value", "")))

    def test_connector_revoke_does_not_cross_identities_or_connectors(self):
        broker = ConnectorBroker()
        broker.grant("owner-service", "mira", ["mira:read"])
        broker.grant("audit-service", "mira", ["mira:read"])
        broker.grant("owner-service", "github", ["github:read"])
        self.assertEqual(broker.revoke_connector("owner-service", "mira"), 1)
        self.assertFalse(broker.authorize("owner-service", "mira", "mira:read"))
        self.assertTrue(broker.authorize("audit-service", "mira", "mira:read"))
        self.assertTrue(broker.authorize("owner-service", "github", "github:read"))

    def test_invalid_scope_connector_and_credential_value_fail_closed(self):
        broker = ConnectorBroker()
        with self.assertRaises(ConnectorAuthorizationError):
            broker.grant("owner-service", "google", ["github:read"])
        with self.assertRaises(ConnectorAuthorizationError):
            broker.grant("owner-service", "unknown", ["unknown:read"])
        with self.assertRaises(ConnectorAuthorizationError):
            broker.grant("owner-service", "cloudflare", ["cloudflare:write"])
        with self.assertRaises(ConnectorAuthorizationError):
            broker.grant("owner-service", "github", ["github:read"], credential_ref="raw secret")

    def test_idempotent_grant_and_unknown_revoke(self):
        broker = ConnectorBroker()
        first = broker.grant("owner-service", "cloudflare", ["cloudflare:read"], grant_id="g1")
        self.assertIs(broker.grant("owner-service", "cloudflare", ["cloudflare:read"], grant_id="g1"), first)
        with self.assertRaises(ConnectorAuthorizationError):
            broker.grant("owner-service", "google", ["google:read"], grant_id="g1")
        with self.assertRaises(ConnectorAuthorizationError):
            broker.revoke("missing")


if __name__ == "__main__":
    unittest.main()
