import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from astra_one.owner_approval import (
    OwnerApprovalError,
    SSH_NAMESPACE,
    prepare_receipt,
    verify_receipt,
)


class OwnerApprovalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.private = self.root / "owner_ed25519"
        subprocess.run(
            ["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(self.private)],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.allowed = self.root / "allowed_signers"
        self.allowed.write_text("owner " + self.private.with_name(self.private.name + ".pub").read_text(), encoding="utf-8")
        os.chmod(self.allowed, 0o600)
        self.receipt = self.root / "approval" / "BASE-008.json"
        self.payload = {
            "task_id": "BASE-008",
            "decision": "APPROVE",
            "owner_identity": "owner",
            "decided_at_utc": "2026-11-15T07:00:00Z",
            "scope": "ten active modules; Business excluded/archived; no release/deployment/cutover",
            "evidence": {
                "packet_sha256": "a" * 64,
                "full_architecture_sha256": "b" * 64,
                "bounded_focus_sha256": "c" * 64,
                "parent_payload_sha256": "d" * 64,
            },
            "packet_sha256": "a" * 64,
            "full_architecture_sha256": "b" * 64,
            "bounded_focus_sha256": "c" * 64,
            "parent_payload_sha256": "d" * 64,
            "source_sha": "e" * 40,
            "integration_sha": "f" * 40,
        }
        prepare_receipt(
            self.payload, receipt_path=self.receipt, allowed_signers=self.allowed,
            message_file="BASE-008.message", signature_file="BASE-008.message.sig",
        )
        subprocess.run(
            ["ssh-keygen", "-Y", "sign", "-f", str(self.private), "-n", SSH_NAMESPACE,
             str(self.receipt.parent / "BASE-008.message")],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        os.chmod(self.receipt.parent / "BASE-008.message.sig", 0o600)

    def tearDown(self):
        self.temp.cleanup()

    def test_signed_receipt_verifies_and_binds_expected_fields(self):
        result = verify_receipt(
            self.receipt, allowed_signers=self.allowed,
            expected={"task_id": "BASE-008", "decision": "APPROVE",
                      "packet_sha256": "a" * 64},
        )
        self.assertEqual(result["principal"], "owner")
        self.assertEqual(result["payload"]["scope"], self.payload["scope"])

    def test_tampered_receipt_is_rejected(self):
        document = json.loads(self.receipt.read_text(encoding="utf-8"))
        document["payload"]["scope"] = "Business included"
        self.receipt.write_text(json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        os.chmod(self.receipt, 0o600)
        with self.assertRaises(OwnerApprovalError):
            verify_receipt(self.receipt, allowed_signers=self.allowed)

    def test_changed_trusted_signer_file_is_rejected(self):
        self.allowed.write_text("owner " + self.private.with_name(self.private.name + ".pub").read_text() + "\n", encoding="utf-8")
        os.chmod(self.allowed, 0o600)
        with self.assertRaises(OwnerApprovalError):
            verify_receipt(self.receipt, allowed_signers=self.allowed)

    def test_receipt_symlink_and_weak_modes_are_rejected(self):
        alias = self.root / "approval" / "alias.json"
        alias.symlink_to(self.receipt.name)
        with self.assertRaises(OwnerApprovalError):
            verify_receipt(alias, allowed_signers=self.allowed)
        alias.unlink()
        os.chmod(self.receipt, 0o640)
        with self.assertRaises(OwnerApprovalError):
            verify_receipt(self.receipt, allowed_signers=self.allowed)
        os.chmod(self.receipt, 0o600)
        os.chmod(self.receipt.parent, 0o755)
        with self.assertRaises(OwnerApprovalError):
            verify_receipt(self.receipt, allowed_signers=self.allowed)


if __name__ == "__main__":
    unittest.main()
