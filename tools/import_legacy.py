#!/usr/bin/env python3
"""Stage committed, pinned legacy code candidates. Dry-run unless --apply."""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess
from pathlib import Path

def git(repo, *args):
    p=subprocess.run(["git","-C",str(repo),*args],capture_output=True,check=True)
    return p.stdout

def safe_relative(value):
    if not isinstance(value, str):
        raise ValueError("path must be a string")
    p=Path(value)
    if not value or p.is_absolute() or any(part in ("", ".", "..") for part in p.parts) or "\\" in value or value.startswith("/"):
        raise ValueError("unsafe path: "+value)
    return p

def _casefold_parts(path):
    return tuple(part.casefold() for part in path.parts)

def _check_existing_path(dest, relative):
    """Reject exact, case-only, and symlinked path collisions without writing."""
    current = dest
    for part in relative.parts:
        if current.is_symlink():
            raise ValueError("symlink in destination path: "+str(relative))
        if not current.is_dir():
            raise FileExistsError(str(current))
        matches = [child for child in current.iterdir() if child.name.casefold() == part.casefold()]
        if matches:
            match = matches[0]
            if match.is_symlink():
                raise ValueError("symlink in destination path: "+str(relative))
            if match.name != part:
                raise FileExistsError(str(dest / relative))
            current = match
        else:
            return
    if current.exists() or current.is_symlink():
        raise FileExistsError(str(dest / relative))

def _validate_commit_pin(value):
    if value is None:
        return
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", value):
        raise ValueError("expected source commit must be a full SHA-1")

def prepare_manifest(repo: Path, dest: Path, manifest: dict, *, apply: bool=False, allow_fixture_origin: bool=False):
    repo=repo.resolve();dest=dest.resolve()
    if not repo.is_dir() or not (repo/".git").exists():raise ValueError("not a cloned Git repository")
    origin=git(repo,"remote","get-url","origin").decode().strip()
    if not allow_fixture_origin and not re.search(r"(?:^|[:/])admindeveloper4562/personal-jarvis(?:\.git)?$",origin):
        raise ValueError("source origin must be the approved legacy repository")
    if not isinstance(manifest, dict) or manifest.get("schema")!="jarvis-v2.legacy-import/1":raise ValueError("wrong manifest schema")
    entries = manifest.get("entries")
    if not isinstance(entries, list): raise ValueError("entries must be a list")
    expected_manifest_commit = manifest.get("expected_source_commit")
    _validate_commit_pin(expected_manifest_commit)
    results=[];writes=[]
    planned_targets = set()
    for entry in entries:
        if not isinstance(entry, dict): raise ValueError("entry must be an object")
        if any(key in entry for key in ("delete", "rename", "execute", "payload")):
            raise ValueError("unsupported create-only entry")
        for key in ("source", "target", "area", "ref"):
            if not isinstance(entry.get(key), str): raise ValueError("invalid entry field: "+key)
        path=safe_relative(entry["source"])
        target=safe_relative(entry["target"])
        if target.parts[:2]!=("migration","imported") or len(target.parts)<4:raise ValueError("must stage under migration/imported")
        if not re.fullmatch(r"[a-z0-9_/-]+",entry["area"]):raise ValueError("invalid area")
        ref=entry["ref"]
        if not re.fullmatch(r"[A-Za-z0-9_./-]{1,128}",ref):raise ValueError("invalid ref")
        expected_commit = entry.get("expected_source_commit", expected_manifest_commit)
        _validate_commit_pin(expected_commit)
        if expected_manifest_commit and expected_commit and expected_manifest_commit.lower() != expected_commit.lower():
            raise ValueError("conflicting expected source commits")
        # Read only remote tracking branch or explicit SHA, never local dirty worktree state.
        commit=git(repo,"rev-parse","--verify",f"refs/remotes/origin/{ref}^{{commit}}").decode().strip()
        if expected_commit and commit.lower() != expected_commit.lower():
            raise ValueError("source commit does not match expected pin")
        tree_row=git(repo,"ls-tree",commit,"--",str(path)).decode().strip()
        if not tree_row or tree_row.split()[0] not in ("100644","100755"):
            raise ValueError("source not a regular tracked file")
        blob=git(repo,"rev-parse",f"{commit}:{path}").decode().strip()
        if git(repo,"cat-file","-t",blob).strip()!=b"blob":raise ValueError("non-blob source rejected")
        data=git(repo,"cat-file","blob",blob)
        if len(data)>1_500_000:raise ValueError("oversized blob rejected")
        candidate=(dest/target).resolve()
        if not candidate.is_relative_to(dest):raise ValueError("destination escaped root")
        folded_target = _casefold_parts(target)
        if folded_target in planned_targets: raise FileExistsError(str(candidate))
        planned_targets.add(folded_target)
        _check_existing_path(dest, target)
        info={"area":entry["area"],"source_ref":ref,"source_commit":commit,"source_path":str(path),"source_blob":blob,"target":str(target),"sha256":hashlib.sha256(data).hexdigest(),"size":len(data),"status":"staged_unreviewed"}
        results.append(info);writes.append((candidate,data))
    if apply:
        log=dest/"migration"/"provenance"/"import-log.json"
        _check_existing_path(dest, Path("migration/provenance/import-log.json"))
        for candidate,data in writes:
            candidate.parent.mkdir(parents=True,exist_ok=True)
            with open(candidate,"xb") as f:f.write(data)
        log.parent.mkdir(parents=True,exist_ok=True)
        with open(log,"x",encoding="utf-8") as f:json.dump({"schema":"jarvis-v2.legacy-provenance/1","entries":results},f,indent=2)
    return {"dry_run":not apply,"count":len(results),"entries":results}

def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",type=Path,required=True,help="clone of approved personal-jarvis repo with remote tracking branches")
    ap.add_argument("--manifest",type=Path,default=Path(__file__).resolve().parents[1]/"config/legacy_import_manifest.json")
    ap.add_argument("--destination",type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument("--apply",action="store_true",help="write new candidate files only; never execute")
    a=ap.parse_args(argv)
    m=json.loads(a.manifest.read_text(encoding="utf-8"))
    report=prepare_manifest(a.repo,a.destination,m,apply=a.apply)
    print(json.dumps({"dry_run":report["dry_run"],"count":report["count"],"preview":report["entries"][:5],"note":"staged_unreviewed, never executable automatically"},indent=2))
if __name__=="__main__":main()
