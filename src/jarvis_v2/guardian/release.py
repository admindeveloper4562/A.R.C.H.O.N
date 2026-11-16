"""Read-only candidate release inspection; this module never deploys anything."""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import json
import re

REQUIRED_GATES = ("independent_qc", "tests", "security", "rollback_ready", "owner_approved", "watchdog_ready")
_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
_EVIDENCE_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_CANARY_EVIDENCE = ("independent_qc", "tests", "security", "rollback")

def inspect(path: Path) -> dict:
    """Verify manifest evidence flags, paths and artifact hash. Not a signature verifier."""
    manifest_path=Path(path)
    data=json.loads(manifest_path.read_text(encoding="utf-8"))
    reasons=[]
    if data.get("schema")!="jarvis-v2.release-candidate/1": reasons.append("unsupported schema")
    if data.get("module") not in {"sda","guardian","core","backend","runtime","research","tws","wic","finance","automation"}:reasons.append("unknown module")
    digest=data.get("sha256","")
    if not isinstance(digest,str) or len(digest)!=64 or any(c not in "0123456789abcdef" for c in digest):reasons.append("invalid digest")
    rel=data.get("artifact","")
    if not isinstance(rel,str) or not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:reasons.append("invalid relative artifact path")
    else:
        raw_candidate=manifest_path.parent / rel
        candidate=raw_candidate.resolve()
        root=manifest_path.parent.resolve()
        if not candidate.is_relative_to(root) or not candidate.is_file():reasons.append("artifact absent or outside manifest directory")
        elif raw_candidate.is_symlink():reasons.append("artifact symlink disallowed")
        elif sha256(candidate.read_bytes()).hexdigest()!=digest:reasons.append("artifact checksum mismatch")
    checks=data.get("gates")
    if not isinstance(checks,dict):reasons.append("missing gates")
    else:reasons.extend("gate not approved: "+key for key in REQUIRED_GATES if checks.get(key) is not True)
    if data.get("module") == "guardian" and not data.get("external_watchdog_identity"):
        reasons.append("guardian must have external watchdog identity")
    if not data.get("previous_healthy_artifact_sha256"):
        reasons.append("missing last-known-good rollback hash")
    return {"eligible_for_independent_review":not reasons,"reasons":reasons,"module":data.get("module"),"artifact_sha256":digest,"deployment_performed":False,"note":"This checks declared evidence flags and checksum only; it does not independently verify signatures, approvals or tests."}


def inspect_canary(path: Path) -> dict:
    """Return a read-only canary decision bound to accepted evidence.

    A canary is only eligible when the existing release gates pass, the
    candidate/base commits are identified, required evidence is referenced,
    and the route remains inactive behind one fenced writer. This function
    never changes routing or starts a candidate.
    """
    manifest_path = Path(path)
    result = inspect(manifest_path)
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        result.update({"eligible_for_canary": False, "canary_reasons": ["manifest_unreadable"]})
        return result

    reasons = list(result["reasons"])
    for field in ("candidate_sha", "base_sha"):
        value = data.get(field)
        if not isinstance(value, str) or not _GIT_SHA.fullmatch(value):
            reasons.append(f"invalid {field}")

    evidence = data.get("evidence_refs")
    if not isinstance(evidence, dict):
        reasons.append("missing canary evidence references")
    else:
        for key in _CANARY_EVIDENCE:
            value = evidence.get(key)
            if not isinstance(value, str) or not _EVIDENCE_REF.fullmatch(value):
                reasons.append(f"invalid {key} evidence reference")

    route_gate = data.get("route_gate")
    if not isinstance(route_gate, dict):
        reasons.append("missing route gate")
    elif route_gate != {"mode": "inactive", "single_writer_fenced": True}:
        reasons.append("route gate is not closed")

    previous = data.get("previous_healthy_artifact_sha256")
    if not isinstance(previous, str) or len(previous) != 64 or any(
        char not in "0123456789abcdef" for char in previous
    ):
        reasons.append("invalid last-known-good artifact hash")

    return {
        **result,
        "eligible_for_canary": not reasons,
        "canary_reasons": reasons,
        "route_switched": False,
    }


__all__ = ["REQUIRED_GATES", "inspect", "inspect_canary"]
