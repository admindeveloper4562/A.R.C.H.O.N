import sqlite3
import tempfile
import unittest
from pathlib import Path

from jarvis_v2.runtime import (
    EMAIL_DRAFT_SCOPE,
    EMAIL_READ_SCOPE,
    EMAIL_SEND_SCOPE,
    EmailAuthorizationError,
    EmailReconciliationRequired,
    EmailService,
    EmailSummary,
    EmailTimeout,
)


class FakeEmail:
    def __init__(self):
        self.calls = []
        self.fail_timeout = False

    def search(self, query, *, limit):
        self.calls.append(("search", query, limit))
        return (EmailSummary("m1", "sender@example.com", "hello", "2026-11-17T00:00:00Z"),)

    def create_draft(self, draft_id, message):
        self.calls.append(("draft", draft_id, message))
        return "draft-ref-1"

    def send(self, send_id, message):
        self.calls.append(("send", send_id, message))
        if self.fail_timeout:
            raise TimeoutError
        return "send-ref-1"


class RuntimeEmailTests(unittest.TestCase):
    def test_scopes_and_owner_approval_gate_operations(self):
        adapter = FakeEmail()
        scopes = {EMAIL_READ_SCOPE, EMAIL_DRAFT_SCOPE, EMAIL_SEND_SCOPE}
        with tempfile.TemporaryDirectory() as directory:
            with EmailService(Path(directory) / "email.sqlite", adapter, lambda scope, digest: scope in scopes) as service:
                self.assertEqual(len(service.search("from:sender")), 1)
                draft = service.create_draft("draft-1", ["owner@example.com"], "hello", "body")
                self.assertEqual(draft.status, "completed")
                with self.assertRaises(EmailAuthorizationError):
                    service.send("send-1", ["owner@example.com"], "hello", "body")
                sent = service.send(
                    "send-1", ["owner@example.com"], "hello", "body", owner_approved=True
                )
                self.assertEqual(sent.provider_ref, "send-ref-1")
            self.assertEqual([call[0] for call in adapter.calls], ["search", "draft", "send"])

    def test_send_receipt_is_idempotent_after_reopen(self):
        adapter = FakeEmail()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "email.sqlite"
            with EmailService(path, adapter, lambda scope, digest: True) as service:
                first = service.send("send-1", ["owner@example.com"], "hello", "body", owner_approved=True)
                second = service.send("send-1", ["owner@example.com"], "hello", "body", owner_approved=True)
                self.assertEqual(first, second)
            with EmailService(path, adapter, lambda scope, digest: True) as reopened:
                self.assertEqual(reopened.send("send-1", ["owner@example.com"], "hello", "body", owner_approved=True), first)
            self.assertEqual([call[0] for call in adapter.calls], ["send"])

    def test_timeout_is_fenced_and_receipt_survives_reconciliation(self):
        adapter = FakeEmail()
        adapter.fail_timeout = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "email.sqlite"
            with EmailService(path, adapter, lambda scope, digest: True) as service:
                with self.assertRaises(EmailTimeout):
                    service.send("send-1", ["owner@example.com"], "hello", "body", owner_approved=True)
            with EmailService(path, adapter, lambda scope, digest: True) as reopened:
                pending = reopened.reconcile()
                self.assertEqual(pending[0]["status"], "needs_reconciliation")
                with self.assertRaises(EmailReconciliationRequired):
                    reopened.send("send-1", ["owner@example.com"], "hello", "body", owner_approved=True)
            self.assertEqual([call[0] for call in adapter.calls], ["send"])

    def test_effect_journal_does_not_store_message_body(self):
        adapter = FakeEmail()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "email.sqlite"
            with EmailService(path, adapter, lambda scope, digest: True) as service:
                service.send("send-1", ["owner@example.com"], "hello", "private body", owner_approved=True)
            db = sqlite3.connect(path)
            request = db.execute("select request_json from tool_effect_journal").fetchone()[0]
            db.close()
            self.assertNotIn("private body", request)
            self.assertNotIn("owner@example.com", request)


if __name__ == "__main__":
    unittest.main()
