import sqlite3
import tempfile
import unittest
from pathlib import Path

from jarvis_v2.runtime import BrowserProfileError, BrowserProfileService


class BrowserProfileServiceTests(unittest.TestCase):
    def make_service(self, root: str):
        return BrowserProfileService(
            Path(root) / "browser.sqlite",
            Path(root) / "profiles",
            site_actions={"example.com": ("read", "publish")},
            read_only_actions=("read",),
        )

    def test_profile_and_human_handoff_persist_without_raw_session_value(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.make_service(directory) as service:
                profile = service.create_profile("work", "example.com")
                self.assertEqual(profile.status, "login_required")
                handoff = service.begin_login("work", "handoff-1")
                self.assertEqual(handoff.status, "awaiting_human")
                completed = service.complete_login("work", "handoff-1", proof_ref="ref:browser-session-1")
                self.assertEqual(completed.status, "completed")
                context = service.get_profile("work").model_context()
                self.assertNotIn("profile_path", context)
                self.assertNotIn("browser-session-1", str(context))
                raw = service.db.execute(
                    "SELECT proof_sha256 FROM browser_login_handoffs WHERE handoff_id='handoff-1'"
                ).fetchone()[0]
                self.assertNotEqual(raw, "ref:browser-session-1")
            with self.make_service(directory) as reopened:
                self.assertEqual(reopened.get_profile("work").status, "ready")
                self.assertTrue(Path(reopened.get_profile("work").profile_path).is_dir())

    def test_actions_are_allowlisted_confirmed_and_target_is_not_retained(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.make_service(directory) as service:
                service.create_profile("work", "example.com")
                service.begin_login("work", "handoff-1")
                service.complete_login("work", "handoff-1", proof_ref="ref:browser-session-1")
                receipt = service.authorize_action(
                    "work", "request-1", action="read", target_ref="page:inbox"
                )
                self.assertEqual(receipt.model_context()["status"], "authorized")
                self.assertNotIn("page:inbox", str(receipt.model_context()))
                with self.assertRaisesRegex(BrowserProfileError, "confirmation"):
                    service.authorize_action(
                        "work", "request-2", action="publish", target_ref="draft:1"
                    )
                confirmed = service.authorize_action(
                    "work", "request-2", action="publish", target_ref="draft:1", confirmed=True
                )
                self.assertTrue(confirmed.confirmed)
                with self.assertRaisesRegex(BrowserProfileError, "allowlisted"):
                    service.authorize_action(
                        "work", "request-3", action="delete", target_ref="draft:1", confirmed=True
                    )
                with self.assertRaisesRegex(BrowserProfileError, "opaque"):
                    service.authorize_action(
                        "work", "request-4", action="read", target_ref="https://example.com/?session=raw"
                    )

    def test_idempotency_and_invalid_login_reference_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.make_service(directory) as service:
                service.create_profile("work", "example.com")
                service.begin_login("work", "handoff-1")
                with self.assertRaisesRegex(BrowserProfileError, "invalid"):
                    service.complete_login("work", "handoff-1", proof_ref="cookie=value")
                service.complete_login("work", "handoff-1", proof_ref="ref:browser-session-1")
                first = service.authorize_action(
                    "work", "request-1", action="read", target_ref="page:inbox"
                )
                self.assertEqual(first, service.authorize_action(
                    "work", "request-1", action="read", target_ref="page:inbox"
                ))
                with self.assertRaisesRegex(BrowserProfileError, "conflict"):
                    service.authorize_action(
                        "work", "request-1", action="read", target_ref="page:other"
                    )


if __name__ == "__main__":
    unittest.main()
