#!/usr/bin/env python3
"""SDA provider-neutral conversation handoff validation.

Do not confuse a portable state packet with resuming a provider-native session.
No provider calls, state writes, tool execution, or account rotation occur here.
"""
from __future__ import annotations

import hashlib
import json
import re

ID = re.compile(r"^[a-zA-Z0-9_:-]{1,100}$")
SHA = re.compile(r"^[0-9a-f]{40,64}$")


class HandoffError(ValueError):
    pass


def build_handoff(state: dict, next_provider: str, *, recent: int = 8) -> dict:
    """Preserve cursor, exact requirements, provenance, and committed receipts."""
    if not isinstance(state, dict) or set(state) != {
            "schema", "conversation_id", "turns", "task",
            "tool_receipts", "last_committed_seq", "active_policy_digest"}:
        raise HandoffError("invalid canonical session snapshot")
    if state["schema"] != 1:
        raise HandoffError("unsupported session schema")
    for field, val in (("conversation_id", state["conversation_id"]),
                       ("next_provider", next_provider)):
        if not isinstance(val, str) or not ID.fullmatch(val):
            raise HandoffError("invalid " + field)
    if type(recent) is not int or not 1 <= recent <= 20:
        raise HandoffError("recent history window must be 1..20")

    policy_digest = state["active_policy_digest"]
    if not isinstance(policy_digest, str) or not SHA.fullmatch(policy_digest):
        raise HandoffError("verified active policy digest is required")
    task = state["task"]
    if not isinstance(task, dict) or set(task) != {
            "task_id", "objective", "acceptance", "git_commit"}:
        raise HandoffError("task checkpoint is missing")
    if not isinstance(task["task_id"], str) or not ID.fullmatch(task["task_id"]):
        raise HandoffError("invalid task id")
    if not isinstance(task["objective"], str) or not 0 < len(task["objective"]) <= 4_000:
        raise HandoffError("invalid task objective")
    if not isinstance(task["acceptance"], list) or not 1 <= len(task["acceptance"]) <= 20:
        raise HandoffError("exact acceptance criteria required")
    if any(not isinstance(x, str) or not 0 < len(x) <= 1_000
           for x in task["acceptance"]):
        raise HandoffError("invalid acceptance criteria")
    if not isinstance(task["git_commit"], str) or not SHA.fullmatch(task["git_commit"]):
        raise HandoffError("pinned source commit required")

    turns = state["turns"]
    if not isinstance(turns, list) or len(turns) > 5_000:
        raise HandoffError("turn history exceeds bounded validation limit")
    if not isinstance(state["last_committed_seq"], int) or (
            type(state["last_committed_seq"]) is not int):
        raise HandoffError("invalid committed sequence")
    if state["last_committed_seq"] != len(turns):
        raise HandoffError("uncommitted or missing conversation turns")
    for i, item in enumerate(turns, 1):
        if not isinstance(item, dict) or set(item) != {"seq", "role", "content"}:
            raise HandoffError("malformed conversation turn")
        if type(item["seq"]) is not int or item["seq"] != i:
            raise HandoffError("missing or duplicated turn sequence")
        if item["role"] not in {"user", "assistant", "tool"}:
            raise HandoffError("unsupported turn role")
        if not isinstance(item["content"], str) or len(item["content"]) > 20_000:
            raise HandoffError("invalid turn content")
    receipts = state["tool_receipts"]
    if not isinstance(receipts, list) or len(receipts) > 500:
        raise HandoffError("invalid tool receipt list")
    seen = set()
    for item in receipts:
        if not isinstance(item, dict) or set(item) != {"call_id", "status"}:
            raise HandoffError("invalid tool receipt")
        if not isinstance(item["call_id"], str) or not ID.fullmatch(item["call_id"]):
            raise HandoffError("invalid tool call id")
        if item["call_id"] in seen or item["status"] not in {"committed", "rejected"}:
            raise HandoffError("pending/duplicated tool effect requires reconciliation")
        seen.add(item["call_id"])

    # Immutable full source-of-truth history can be stored locally; the routing
    # packet merely references its digest and carries a bounded recent view.
    serialized = json.dumps(turns, sort_keys=True, separators=(",", ":")).encode()
    digest = hashlib.sha256(serialized).hexdigest()
    return {
        "schema": 1,
        "kind": "provider_neutral_handoff",
        "conversation_id": state["conversation_id"],
        "resume_after_seq": state["last_committed_seq"],
        "full_history_sha256": digest,
        "recent_turns": turns[-recent:],
        "task": task,
        "policy_digest": policy_digest,
        "tool_receipts": receipts,
        "target_provider": next_provider,
        "native_session_resumed": False,
        "tool_calls_replayed": False,
        "requires_source_history_available": True,
        "requires_provider_capability_check": True,
    }


def verify_handoff(packet: dict, history: list[dict], *,
                   provider: str, policy_digest: str) -> bool:
    """Validate continuity against the canonical full history and policy."""
    if packet.get("kind") != "provider_neutral_handoff":
        return False
    if packet.get("target_provider") != provider:
        return False
    if packet.get("policy_digest") != policy_digest:
        return False
    try:
        canonical = json.dumps(history, sort_keys=True, separators=(",", ":")).encode()
    except (TypeError, ValueError):
        return False
    return (
        hashlib.sha256(canonical).hexdigest() == packet.get("full_history_sha256")
        and len(history) == packet.get("resume_after_seq")
        and packet.get("native_session_resumed") is False
        and packet.get("tool_calls_replayed") is False
    )
