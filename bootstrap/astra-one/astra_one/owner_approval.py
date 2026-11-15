"""Digest-bound owner approvals using detached OpenSSH signatures.

The private signing key never enters Astra state.  The operator provisions an
``allowed_signers`` file out of band, the owner signs the canonical receipt
message with ``ssh-keygen -Y sign``, and the deterministic Master verifies the
signature before changing a task state.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Mapping


SCHEMA = "archon.owner-approval/1"
SSH_ALGORITHM = "ssh-ed25519"
SSH_NAMESPACE = "archon-owner-approval-v1"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
PRINCIPAL = re.compile(r"^[A-Za-z0-9_.@+-]{1,128}$")
DECISIONS = frozenset({"APPROVE", "REJECT", "DEFER"})
REQUIRED_PAYLOAD_FIELDS = frozenset({
    "task_id", "decision", "owner_identity", "decided_at_utc", "scope", "evidence",
})


class OwnerApprovalError(ValueError):
    """Raised for malformed, untrusted or unverifiable owner receipts."""


def _canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False) + "\n").encode("utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _secure_file(path: Path, *, label: str) -> None:
    try:
        info = path.lstat()
    except OSError as exc:
        raise OwnerApprovalError(f"{label} unavailable") from exc
    if not path.is_file() or path.is_symlink():
        raise OwnerApprovalError(f"{label} must be a regular non-symlink file")
    if info.st_uid != os.getuid():
        raise OwnerApprovalError(f"{label} is not owned by the current user")
    if (info.st_mode & 0o777) != 0o600:
        raise OwnerApprovalError(f"{label} must have mode 0600")


def _secure_directory(path: Path, *, label: str) -> None:
    try:
        info = path.lstat()
    except OSError as exc:
        raise OwnerApprovalError(f"{label} unavailable") from exc
    if not path.is_dir() or path.is_symlink():
        raise OwnerApprovalError(f"{label} must be a regular non-symlink directory")
    if info.st_uid != os.getuid() or (info.st_mode & 0o777) != 0o700:
        raise OwnerApprovalError(f"{label} must be owner-private mode 0700")


def _secure_directory_chain(path: Path, *, root: Path | None = None) -> None:
    directory = path.absolute()
    trusted_root = root.absolute() if root is not None else None
    if trusted_root is not None:
        try:
            directory.relative_to(trusted_root)
        except ValueError as exc:
            raise OwnerApprovalError("receipt directory is outside trusted state root") from exc
    while True:
        _secure_directory(directory, label="receipt directory")
        if trusted_root is None or directory == trusted_root:
            break
        if directory == directory.parent:
            raise OwnerApprovalError("trusted state root was not reached")
        directory = directory.parent


def _ensure_private_directory(path: Path) -> None:
    missing: list[Path] = []
    current = path
    while not current.exists():
        missing.append(current)
        if current == current.parent:
            break
        current = current.parent
    for directory in reversed(missing):
        directory.mkdir(mode=0o700)


def _safe_child(parent: Path, value: object, *, label: str) -> Path:
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise OwnerApprovalError(f"invalid {label}")
    raw = parent / value
    if raw.is_symlink():
        raise OwnerApprovalError(f"{label} must not be a symlink")
    candidate = raw.resolve()
    try:
        candidate.relative_to(parent.resolve())
    except ValueError as exc:
        raise OwnerApprovalError(f"{label} escapes receipt directory") from exc
    return candidate


def _validate_payload(payload: object) -> dict[str, Any]:
    if not isinstance(payload, dict) or not REQUIRED_PAYLOAD_FIELDS.issubset(payload):
        raise OwnerApprovalError("owner receipt payload is incomplete")
    task_id = payload.get("task_id")
    if not isinstance(task_id, str) or not re.fullmatch(r"[A-Z][A-Z0-9-]{2,47}", task_id):
        raise OwnerApprovalError("invalid owner receipt task ID")
    if payload.get("decision") not in DECISIONS:
        raise OwnerApprovalError("invalid owner receipt decision")
    identity = payload.get("owner_identity")
    if not isinstance(identity, str) or not PRINCIPAL.fullmatch(identity):
        raise OwnerApprovalError("invalid owner identity")
    decided = payload.get("decided_at_utc")
    if not isinstance(decided, str) or not decided.endswith("Z"):
        raise OwnerApprovalError("owner decision timestamp must be UTC")
    try:
        timestamp = dt.datetime.fromisoformat(decided[:-1] + "+00:00")
    except ValueError as exc:
        raise OwnerApprovalError("invalid owner decision timestamp") from exc
    if timestamp.tzinfo is None or timestamp.utcoffset() != dt.timedelta(0):
        raise OwnerApprovalError("owner decision timestamp must be UTC")
    if not isinstance(payload.get("scope"), str) or not payload["scope"].strip():
        raise OwnerApprovalError("owner receipt scope is required")
    if not isinstance(payload.get("evidence"), dict) or not payload["evidence"]:
        raise OwnerApprovalError("owner receipt evidence references are required")
    return payload


def _document(receipt: Mapping[str, Any]) -> dict[str, Any]:
    if set(receipt) != {"schema", "payload", "signature"}:
        raise OwnerApprovalError("owner receipt has unexpected top-level fields")
    if receipt.get("schema") != SCHEMA:
        raise OwnerApprovalError("owner receipt schema mismatch")
    payload = _validate_payload(receipt.get("payload"))
    signature = receipt.get("signature")
    if not isinstance(signature, dict):
        raise OwnerApprovalError("owner receipt signature metadata missing")
    required = {"algorithm", "namespace", "principal", "allowed_signers_sha256",
                "message_file", "signature_file"}
    if set(signature) != required:
        raise OwnerApprovalError("owner receipt signature metadata is incomplete")
    if signature["algorithm"] != SSH_ALGORITHM or signature["namespace"] != SSH_NAMESPACE:
        raise OwnerApprovalError("owner receipt signature algorithm or namespace mismatch")
    if signature["principal"] != payload["owner_identity"]:
        raise OwnerApprovalError("owner identity and signature principal differ")
    if not PRINCIPAL.fullmatch(str(signature["principal"])):
        raise OwnerApprovalError("invalid signature principal")
    if not HEX64.fullmatch(str(signature["allowed_signers_sha256"])):
        raise OwnerApprovalError("invalid allowed-signers digest")
    return {"schema": receipt["schema"], "payload": payload, "signature": signature}


def prepare_receipt(
    payload: Mapping[str, Any],
    *,
    receipt_path: Path,
    allowed_signers: Path,
    message_file: str,
    signature_file: str,
    trusted_root: Path | None = None,
) -> dict[str, str]:
    """Write an unsigned receipt and its exact signing message."""
    _secure_file(allowed_signers, label="allowed signers file")
    checked_payload = _validate_payload(dict(payload))
    _principal_is_allowed(allowed_signers, checked_payload["owner_identity"])
    if not message_file or not signature_file:
        raise OwnerApprovalError("signature file names are required")
    receipt_path = receipt_path.expanduser()
    if not receipt_path.is_absolute():
        receipt_path = receipt_path.absolute()
    if receipt_path.exists() or receipt_path.is_symlink():
        raise OwnerApprovalError("owner receipt already exists")
    _ensure_private_directory(receipt_path.parent)
    _secure_directory_chain(receipt_path.parent, root=trusted_root)
    message_path = _safe_child(receipt_path.parent, message_file, label="message file")
    signature_path = _safe_child(receipt_path.parent, signature_file, label="signature file")
    if message_path.exists() or message_path.is_symlink() or signature_path.exists() or signature_path.is_symlink():
        raise OwnerApprovalError("owner receipt message or signature already exists")
    receipt = {
        "schema": SCHEMA,
        "payload": checked_payload,
        "signature": {
            "algorithm": SSH_ALGORITHM,
            "namespace": SSH_NAMESPACE,
            "principal": checked_payload["owner_identity"],
            "allowed_signers_sha256": _sha256(allowed_signers),
            "message_file": message_file,
            "signature_file": signature_file,
        },
    }
    document = _document(receipt)
    message_path.write_bytes(_canonical(document))
    os.chmod(message_path, 0o600)
    receipt_path.write_bytes(_canonical(receipt))
    os.chmod(receipt_path, 0o600)
    return {"receipt": str(receipt_path), "message": str(message_path),
            "allowed_signers_sha256": receipt["signature"]["allowed_signers_sha256"]}


def _principal_is_allowed(allowed_signers: Path, principal: str) -> None:
    result = subprocess.run(
        ["ssh-keygen", "-Y", "match-principals", "-I", principal,
         "-f", str(allowed_signers)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False, timeout=10,
    )
    if result.returncode != 0:
        raise OwnerApprovalError("owner principal is not present in the trusted signer file")


def verify_receipt(
    receipt_path: Path,
    *,
    allowed_signers: Path,
    expected: Mapping[str, object] | None = None,
    trusted_root: Path | None = None,
) -> dict[str, Any]:
    """Verify a signed receipt and optional exact field bindings."""
    _secure_file(receipt_path, label="owner receipt")
    _secure_file(allowed_signers, label="allowed signers file")
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise OwnerApprovalError("owner receipt is not valid UTF-8 JSON") from exc
    document = _document(receipt)
    payload = document["payload"]
    signature = document["signature"]
    if expected:
        for key, value in expected.items():
            if payload.get(key) != value:
                raise OwnerApprovalError(f"owner receipt binding mismatch: {key}")
    if signature["allowed_signers_sha256"] != _sha256(allowed_signers):
        raise OwnerApprovalError("trusted signer file changed after receipt preparation")
    _principal_is_allowed(allowed_signers, signature["principal"])
    parent = receipt_path.resolve().parent
    _secure_directory_chain(parent, root=trusted_root)
    message_path = _safe_child(parent, signature["message_file"], label="message file")
    signature_path = _safe_child(parent, signature["signature_file"], label="signature file")
    _secure_file(message_path, label="owner signing message")
    _secure_file(signature_path, label="owner signature")
    if message_path.read_bytes() != _canonical(document):
        raise OwnerApprovalError("signed message does not match owner receipt")
    result = subprocess.run(
        ["ssh-keygen", "-Y", "verify", "-f", str(allowed_signers),
         "-I", signature["principal"], "-n", SSH_NAMESPACE, "-s", str(signature_path)],
        input=message_path.read_bytes(), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False, timeout=10,
    )
    if result.returncode != 0:
        raise OwnerApprovalError("owner receipt signature verification failed")
    return {"receipt": str(receipt_path), "payload": payload,
            "allowed_signers_sha256": signature["allowed_signers_sha256"],
            "signature_algorithm": signature["algorithm"],
            "principal": signature["principal"]}


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Prepare or verify an Astra owner approval receipt")
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("--payload", type=Path, required=True,
                         help="UTF-8 JSON object containing the owner decision payload")
    prepare.add_argument("--receipt", type=Path, required=True)
    prepare.add_argument("--allowed-signers", type=Path, required=True)
    prepare.add_argument("--message-file", default="owner-approval.message")
    prepare.add_argument("--signature-file", default="owner-approval.message.sig")
    verify = sub.add_parser("verify")
    verify.add_argument("receipt", type=Path)
    verify.add_argument("--allowed-signers", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            payload = json.loads(args.payload.read_text(encoding="utf-8"))
            result = prepare_receipt(
                payload, receipt_path=args.receipt, allowed_signers=args.allowed_signers,
                message_file=args.message_file, signature_file=args.signature_file,
            )
        else:
            result = verify_receipt(args.receipt, allowed_signers=args.allowed_signers)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (OSError, OwnerApprovalError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(f"owner approval rejected: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
