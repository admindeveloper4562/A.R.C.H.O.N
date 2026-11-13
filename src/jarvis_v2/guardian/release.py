"""Read-only candidate release inspection; this module never deploys anything."""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import json

REQUIRED_GATES = ("independent_qc", "tests", "security", "rollback_ready", "owner_approved", "watchdog_ready")

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
