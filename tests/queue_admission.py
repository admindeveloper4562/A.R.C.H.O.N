from __future__ import annotations

import base64
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import time

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from jarvis_v2 import native_executor


_TEST_OWNER = Ed25519PrivateKey.generate()
_TEST_OWNER_PUBLIC_KEY = _TEST_OWNER.public_key().public_bytes(
    serialization.Encoding.Raw, serialization.PublicFormat.Raw,
)
_TEST_KEY_DIRECTORY = tempfile.TemporaryDirectory(prefix="archon-test-owner-")
_TEST_KEY_STORE = Path(_TEST_KEY_DIRECTORY.name) / "owner-keys.json"
_TEST_KEY_STORE.write_text(json.dumps({
    "schema": 1,
    "keys": {"test-owner": base64.b64encode(_TEST_OWNER_PUBLIC_KEY).decode("ascii")},
}))
_TEST_KEY_STORE.chmod(0o600)
native_executor.OWNER_KEYS_PATH = _TEST_KEY_STORE


def signed_admission(
    *, task_id: str, priority: str, module: str, payload: dict, trusted_signer: bool = True,
) -> dict[str, object]:
    signer = _TEST_OWNER if trusted_signer else Ed25519PrivateKey.generate()
    task = {"task_id": task_id, "priority": priority, "module": module, "payload": payload}
    task_bytes = json.dumps(
        task, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode("utf-8")
    claims = {
        "schema": 1,
        "approval_id": f"test-{sha256(task_id.encode()).hexdigest()[:24]}",
        "key_id": "test-owner",
        "task_id": task_id,
        "operation": "task_submit",
        "target": task_id,
        "content_sha256": sha256(task_bytes).hexdigest(),
        "expires_at": int(time.time()) + 300,
        "decision": "APPROVE",
    }
    signed = json.dumps(claims, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return dict(claims, signature=base64.b64encode(signer.sign(signed)).decode("ascii"))


def enqueue_approved(
    queue,
    *, task_id: str, priority: str, module: str, payload: dict,
    trusted_signer: bool = True,
):
    approval = signed_admission(
        task_id=task_id, priority=priority, module=module, payload=payload,
        trusted_signer=trusted_signer,
    )
    return queue.enqueue(
        task_id=task_id, priority=priority, module=module, payload=payload,
        approval=approval,
    )


def signed_cancellation(task_id: str, *, trusted_signer: bool = True) -> dict[str, object]:
    signer = _TEST_OWNER if trusted_signer else Ed25519PrivateKey.generate()
    claims = {
        "schema": 1,
        "approval_id": f"cancel-{sha256(task_id.encode()).hexdigest()[:24]}",
        "key_id": "test-owner",
        "task_id": task_id,
        "operation": "task_cancel",
        "target": task_id,
        "content_sha256": sha256(task_id.encode("utf-8")).hexdigest(),
        "expires_at": int(time.time()) + 300,
        "decision": "APPROVE",
    }
    message = json.dumps(claims, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return dict(claims, signature=base64.b64encode(signer.sign(message)).decode("ascii"))
