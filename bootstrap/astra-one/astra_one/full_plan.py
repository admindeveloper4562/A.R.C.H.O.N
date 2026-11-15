"""Validation and normalization for the reviewed JARVIS v2 parent/child plan.

The plan is an immutable input.  This module never changes the source files and
does not create queue records; :mod:`linux_sda` owns the transactional import.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any


EXPECTED_MODULES = (
    "BASE", "SDA", "MIG", "CORE", "BACK", "AUTO", "WIN",
    "GUARD", "RUN", "RES", "TWS", "WIC", "FIN", "REL",
)
EXPECTED_PARENT_COUNT = 247
EXPECTED_SUBTASK_COUNT = 1359
EXPECTED_PARENT_BLOB_SHA = "36e674f4e58fc19aa8158da42d802b9599a23763"
PROJECT_ID = "ARCHON-JARVIS-V2"
TASK_MARKDOWN_FORMAT = "archon-task-md-v1"
OWNER_GATE_IDS = (
    "BASE-008", "BASE-016", "SDA-027", "MIG-012", "FIN-001",
    "FIN-016", "REL-018", "REL-020", "REL-021",
)


class PlanValidationError(ValueError):
    """The immutable plan cannot be safely imported."""


def _json(path: Path) -> tuple[bytes, Any]:
    try:
        raw = path.read_bytes()
        return raw, json.loads(raw)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PlanValidationError(f"cannot read plan file: {path}") from exc


def git_blob_sha(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()


def payload_sha(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PlanValidationError(message)


@dataclass(frozen=True)
class FullPlan:
    project: dict[str, Any]
    parents: tuple[dict[str, Any], ...]
    children: dict[str, tuple[dict[str, Any], ...]]
    parent_plan_blob_sha: str
    subtask_index_sha: str
    module_hashes: dict[str, str]
    validation: dict[str, Any]


def _markdown_text(value: object) -> str:
    """Keep task prose on one reviewable Markdown line."""
    text = str(value or "none").replace("\r", " ").replace("\n", " ")
    return text.replace("`", "\\`").strip() or "none"


def _task_markdown_manifest(project: dict[str, Any], parents: list[dict[str, Any]]) -> dict[str, Any]:
    parent_records = []
    child_records = []
    seen_parents: set[str] = set()
    seen_children: set[str] = set()
    for parent in parents:
        spec = parent.get("spec", parent)
        task_id = str(parent.get("task_id") or spec.get("task_id") or "")
        if not task_id or task_id in seen_parents:
            raise PlanValidationError("TASK.md contains duplicate or empty parent ID")
        seen_parents.add(task_id)
        children = parent.get("children", spec.get("subtasks", []))
        dependencies = list(parent.get("dependencies", spec.get("depends_on", [])))
        parent_records.append({
            "id": task_id,
            "payload_sha": parent.get("payload_sha") or payload_sha(spec),
            "dependencies": dependencies,
        })
        for child in children:
            child_id = child.get("id")
            if not isinstance(child_id, str) or not child_id or child_id in seen_children:
                raise PlanValidationError("TASK.md contains duplicate or empty child ID")
            if child.get("parent_id", task_id) != task_id:
                raise PlanValidationError(f"child {child_id} is attached to the wrong parent")
            seen_children.add(child_id)
            child_records.append({
                "id": child_id,
                "parent_id": task_id,
                "sequence": child.get("sequence"),
                "depends_on": list(child.get("depends_on", [])),
                "payload_sha": child.get("payload_sha") or payload_sha(child),
            })
    return {
        "format": TASK_MARKDOWN_FORMAT,
        "project_id": project.get("project_id", PROJECT_ID),
        "project_payload_sha": project.get("payload_sha", ""),
        "parent_count": len(parent_records),
        "child_count": len(child_records),
        "parents": parent_records,
        "children": child_records,
    }


def render_task_markdown(project: dict[str, Any], parents: list[dict[str, Any]], *,
                         statuses: dict[str, str] | None = None,
                         source_path: str = "") -> str:
    """Render a reviewable task view while retaining a verifiable ID manifest."""
    statuses = statuses or {}
    manifest = _task_markdown_manifest(project, parents)
    lines = [
        f"# {project.get('project_name', 'ARCHON project')} Task Plan",
        "",
        f"<!-- {TASK_MARKDOWN_FORMAT} -->",
        "",
        f"- Project: `{_markdown_text(manifest['project_id'])}`",
        f"- Source: `{_markdown_text(project.get('source_repository', ''))}`",
        f"- Integration branch: `{_markdown_text(project.get('integration_branch', ''))}`",
        f"- Parent tasks: {manifest['parent_count']}",
        f"- Child subtasks: {manifest['child_count']}",
        f"- Parent-plan blob SHA: `{_markdown_text(project.get('parent_plan_blob_sha', ''))}`",
        f"- Subtask-index SHA-256: `{_markdown_text(project.get('subtask_index_sha256', ''))}`",
        f"- SQLite authoritative source: `{_markdown_text(source_path or 'not embedded')}`",
        "- This is a reviewable planning view; SQLite remains the authoritative queue.",
        "",
    ]
    for parent in parents:
        spec = parent.get("spec", parent)
        task_id = str(parent.get("task_id") or spec.get("task_id"))
        dependencies = parent.get("dependencies", spec.get("depends_on", []))
        children = parent.get("children", spec.get("subtasks", []))
        lines.extend([
            f"## {task_id} — {_markdown_text(spec.get('title', spec.get('objective', '')))}",
            "",
            f"- State: `{_markdown_text(statuses.get(task_id, 'not_recorded'))}`",
            f"- Module/milestone/priority: `{_markdown_text(parent.get('module', spec.get('module', '')))}` / "
            f"`{_markdown_text(parent.get('milestone', spec.get('milestone', '')))}` / "
            f"`{_markdown_text(parent.get('priority', spec.get('priority', '')))}`",
            f"- Dependencies: {_markdown_text(', '.join(dependencies) if dependencies else 'none')}",
            f"- Owner gate: `{ 'required' if parent.get('owner_gate', spec.get('required_owner_gate', False)) else 'no' }`",
            f"- Execution mode: `{_markdown_text(spec.get('execution_mode', 'worker'))}`",
            f"- Scope roots: {_markdown_text(', '.join(spec.get('suggested_scope_roots', [])) or 'none')}",
            f"- Permissions/guardrails: {_markdown_text('; '.join(spec.get('module_guardrails', [])) or 'bounded task scope')}",
            f"- Objective: {_markdown_text(spec.get('objective', spec.get('title', '')))}",
            f"- Acceptance: {_markdown_text('; '.join(spec.get('acceptance', [])))}",
            f"- Tests/verification: {_markdown_text('; '.join(child.get('done_when', '') for child in children) or 'task acceptance')}",
            f"- Special instructions: {_markdown_text('; '.join(spec.get('special_instructions', [])) or 'none')}",
            f"- Completion rule: {_markdown_text(spec.get('completion_rule', 'all required child evidence and independent QC'))}",
            f"- Reuse notes: {_markdown_text(spec.get('reuse_notes', ''))}",
            "### Child execution packet",
            "",
        ])
        for child in children:
            child_deps = child.get("depends_on", [])
            lines.extend([
                f"- `{child['id']}` sequence {child.get('sequence')} [{_markdown_text(child.get('kind', ''))}] — "
                f"{_markdown_text(child.get('title', ''))}",
                f"  - Instruction: {_markdown_text(child.get('instruction', ''))}",
                f"  - Deliverable: {_markdown_text(child.get('deliverable', ''))}",
                f"  - Done when: {_markdown_text(child.get('done_when', ''))}",
                f"  - Assignee: {_markdown_text(child.get('assignee_role', ''))}; depends on: "
                f"{_markdown_text(', '.join(child_deps) if child_deps else 'none')}; evidence required: "
                f"`{bool(child.get('evidence_required'))}`",
            ])
        lines.append("")
    lines.extend([
        "## Machine validation",
        "",
        "The following manifest is generated from the same SQLite payloads shown above. It is validation metadata, not a queue.",
        "",
        "```json",
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
        "```",
        "",
    ])
    return "\n".join(lines)


def parse_task_markdown(text: str) -> dict[str, Any]:
    """Parse and validate the bounded machine manifest embedded in TASK.md."""
    if not isinstance(text, str) or len(text.encode("utf-8")) > 5_000_000:
        raise PlanValidationError("TASK.md is missing or exceeds the size limit")
    marker = "## Machine validation\n"
    start = text.find(marker)
    if start < 0:
        raise PlanValidationError("TASK.md machine validation section is missing")
    fenced = text.find("```json\n", start)
    if fenced < 0:
        raise PlanValidationError("TASK.md machine validation JSON is missing")
    payload_start = fenced + len("```json\n")
    payload_end = text.find("\n```", payload_start)
    if payload_end < 0:
        raise PlanValidationError("TASK.md machine validation JSON is not fenced")
    try:
        manifest = json.loads(text[payload_start:payload_end])
    except json.JSONDecodeError as exc:
        raise PlanValidationError("TASK.md machine validation JSON is invalid") from exc
    if not isinstance(manifest, dict) or manifest.get("format") != TASK_MARKDOWN_FORMAT:
        raise PlanValidationError("TASK.md machine validation format is unsupported")
    parents = manifest.get("parents")
    children = manifest.get("children")
    if not isinstance(parents, list) or not isinstance(children, list):
        raise PlanValidationError("TASK.md machine validation records are missing")
    parent_ids = [item.get("id") for item in parents if isinstance(item, dict)]
    child_ids = [item.get("id") for item in children if isinstance(item, dict)]
    if len(parent_ids) != len(parents) or len(child_ids) != len(children):
        raise PlanValidationError("TASK.md machine validation records are malformed")
    if len(parent_ids) != len(set(parent_ids)) or len(child_ids) != len(set(child_ids)):
        raise PlanValidationError("TASK.md machine validation IDs are not unique")
    if manifest.get("parent_count") != len(parents) or manifest.get("child_count") != len(children):
        raise PlanValidationError("TASK.md machine validation counts do not match")
    parent_set = set(parent_ids)
    parent_deps = {item["id"]: item.get("dependencies", []) for item in parents}
    if any(not isinstance(deps, list) or any(dep not in parent_set for dep in deps)
           for deps in parent_deps.values()):
        raise PlanValidationError("TASK.md machine validation has an unknown parent dependency")
    indegree = {task_id: len(deps) for task_id, deps in parent_deps.items()}
    dependents = {task_id: [] for task_id in parent_set}
    for task_id, deps in parent_deps.items():
        for dependency in deps:
            dependents[dependency].append(task_id)
    ready = [task_id for task_id, degree in indegree.items() if degree == 0]
    visited = 0
    while ready:
        current = ready.pop(0)
        visited += 1
        for dependent in dependents[current]:
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                ready.append(dependent)
    if visited != len(parent_set):
        raise PlanValidationError("TASK.md machine validation contains a dependency cycle")
    children_by_parent: dict[str, list[dict[str, Any]]] = {task_id: [] for task_id in parent_set}
    for child in children:
        if not isinstance(child, dict) or child.get("parent_id") not in parent_set:
            raise PlanValidationError("TASK.md machine validation has an unknown child parent")
        children_by_parent[child["parent_id"]].append(child)
    for task_id, records in children_by_parent.items():
        records.sort(key=lambda item: item.get("sequence", 0))
        sequences = [item.get("sequence") for item in records]
        if sequences != list(range(1, len(records) + 1)):
            raise PlanValidationError(f"TASK.md machine validation has invalid child order for {task_id}")
        child_set = {item["id"] for item in records}
        for record in records:
            deps = record.get("depends_on", [])
            if not isinstance(deps, list) or any(dep not in child_set for dep in deps):
                raise PlanValidationError(f"TASK.md machine validation has an unknown child dependency for {task_id}")
    return manifest


def validate_task_markdown(text: str, project: dict[str, Any],
                          parents: list[dict[str, Any]]) -> dict[str, Any]:
    """Prove that a TASK.md view still identifies the exact persisted plan."""
    actual = parse_task_markdown(text)
    expected = _task_markdown_manifest(project, parents)
    if actual != expected:
        raise PlanValidationError("TASK.md does not round-trip to the authoritative task payload")
    return {
        "format": TASK_MARKDOWN_FORMAT,
        "project_id": expected["project_id"],
        "parent_count": expected["parent_count"],
        "child_count": expected["child_count"],
        "validated": True,
    }


def load_full_plan(parent_path: Path, index_path: Path, module_dir: Path,
                   *, source_ref: str = "", source_commit: str = "") -> FullPlan:
    parent_raw, parent_doc = _json(parent_path)
    index_raw, index_doc = _json(index_path)
    _require(isinstance(parent_doc, dict) and isinstance(index_doc, dict),
             "parent plan and subtask index must be JSON objects")

    parent_blob = git_blob_sha(parent_raw)
    _require(parent_blob == EXPECTED_PARENT_BLOB_SHA,
             f"parent plan Git blob SHA mismatch: {parent_blob}")
    _require(index_doc.get("source_parent_plan_blob_sha") == parent_blob,
             "subtask index does not pin the parent-plan blob SHA")
    parents = parent_doc.get("tasks")
    _require(isinstance(parents, list) and len(parents) == EXPECTED_PARENT_COUNT,
             "parent plan must contain exactly 247 tasks")
    _require(parent_doc.get("task_count") == EXPECTED_PARENT_COUNT,
             "parent plan task_count is not 247")
    _require(parent_doc.get("business_module_active") is False,
             "Business must remain excluded")
    parent_ids = [p.get("id") for p in parents]
    _require(all(isinstance(x, str) and x for x in parent_ids),
             "every parent must have an ID")
    _require(len(set(parent_ids)) == EXPECTED_PARENT_COUNT,
             "parent IDs are not unique")
    parent_map = {p["id"]: p for p in parents}

    module_entries = index_doc.get("module_files")
    _require(isinstance(module_entries, list), "subtask index module_files is missing")
    entries = {entry.get("module"): entry for entry in module_entries
               if isinstance(entry, dict)}
    _require(tuple(entries) == EXPECTED_MODULES,
             "subtask index must contain the exact 14 workstreams")

    expanded: dict[str, dict[str, Any]] = {}
    children: dict[str, tuple[dict[str, Any], ...]] = {}
    module_hashes: dict[str, str] = {}
    module_counts: dict[str, dict[str, int]] = {}
    for module in EXPECTED_MODULES:
        entry = entries[module]
        relative = entry.get("path")
        _require(isinstance(relative, str) and relative == f"docs/tasks/subtasks/{module}.json",
                 f"unexpected {module} subtask path")
        path = module_dir / f"{module}.json"
        raw, document = _json(path)
        _require(isinstance(document, dict), f"{module} subtask file is not an object")
        module_hashes[module] = hashlib.sha256(raw).hexdigest()
        _require(document.get("source_parent_plan_blob_sha") == parent_blob,
                 f"{module} does not pin the parent-plan blob SHA")
        records = document.get("parents")
        _require(isinstance(records, list), f"{module} parents is missing")
        _require(document.get("module") == module, f"{module} module identity mismatch")
        _require(document.get("parent_count") == len(records), f"{module} parent count mismatch")
        module_child_count = 0
        for expanded_parent in records:
            pid = expanded_parent.get("parent_id")
            _require(isinstance(pid, str) and pid in parent_map,
                     f"{module} references an unknown parent")
            _require(pid not in expanded, f"duplicate expanded parent: {pid}")
            expanded[pid] = expanded_parent
            top = parent_map[pid]
            for field, top_field in (
                ("module", "module"), ("milestone", "milestone"),
                ("priority", "priority"), ("title", "title"),
                ("acceptance", "acceptance"),
            ):
                _require(expanded_parent.get(field) == top.get(top_field),
                         f"{pid} {field} differs between parent and child plans")
            _require(expanded_parent.get("parent_dependencies") == top.get("dependencies"),
                     f"{pid} dependencies differ between parent and child plans")
            _require(expanded_parent.get("status") in {"NOT_STARTED", "NOT_VERIFIED"},
                     f"{pid} has an unsupported expanded status")
            child_records = expanded_parent.get("subtasks")
            _require(isinstance(child_records, list) and child_records,
                     f"{pid} has no child subtasks")
            ids = [child.get("id") for child in child_records]
            _require(len(ids) == len(set(ids)), f"{pid} child IDs are not unique")
            _require([child.get("sequence") for child in child_records] == list(range(1, len(ids) + 1)),
                     f"{pid} child sequence is not contiguous")
            id_set = set(ids)
            for child in child_records:
                cid = child.get("id")
                _require(isinstance(cid, str) and cid.startswith(pid + "."),
                         f"{cid} is attached to the wrong parent")
                for key in ("kind", "title", "instruction", "deliverable", "done_when", "assignee_role"):
                    _require(isinstance(child.get(key), str) and child[key].strip(),
                             f"{cid} has no bounded {key}")
                _require(isinstance(child.get("depends_on"), list), f"{cid} dependency list missing")
                for dependency in child["depends_on"]:
                    _require(dependency in id_set, f"{cid} references unknown child {dependency}")
                    _require(ids.index(dependency) < ids.index(cid),
                             f"{cid} has a forward child dependency")
                _require(isinstance(child.get("evidence_required"), bool),
                         f"{cid} evidence_required is not boolean")
                _require(child.get("remote_github_actions_allowed") is False,
                         f"{cid} permits remote GitHub Actions")
            children[pid] = tuple(child_records)
            module_child_count += len(child_records)
        module_counts[module] = {
            "parents": len(records),
            "children": module_child_count,
            "declared_parents": int(entry.get("parent_count", -1)),
            "declared_children": int(entry.get("subtask_count", -1)),
        }
        _require(module_counts[module]["parents"] == module_counts[module]["declared_parents"],
                 f"{module} declared parent count mismatch")
        _require(module_counts[module]["children"] == module_counts[module]["declared_children"],
                 f"{module} declared child count mismatch")

    _require(set(expanded) == set(parent_map), "expanded parent set differs from source parent set")
    _require(sum(x["children"] for x in module_counts.values()) == EXPECTED_SUBTASK_COUNT,
             "expanded plan must contain exactly 1,359 children")
    _require(index_doc.get("total_subtasks") == EXPECTED_SUBTASK_COUNT,
             "subtask index total_subtasks is not 1,359")
    _require(index_doc.get("business_module_active") is False,
             "subtask index enables Business")

    indegree = {pid: 0 for pid in parent_map}
    edges: dict[str, list[str]] = {pid: [] for pid in parent_map}
    edge_count = 0
    for parent in parents:
        for dependency in parent.get("dependencies", []):
            _require(dependency in parent_map, f"{parent['id']} has unknown dependency {dependency}")
            indegree[parent["id"]] += 1
            edges[dependency].append(parent["id"])
            edge_count += 1
    ready = [pid for pid, count in indegree.items() if count == 0]
    topological: list[str] = []
    while ready:
        current = ready.pop(0)
        topological.append(current)
        for dependent in edges[current]:
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                ready.append(dependent)
    _require(len(topological) == EXPECTED_PARENT_COUNT, "parent dependency graph contains a cycle")

    normalized: list[dict[str, Any]] = []
    for top in parents:
        pid = top["id"]
        expanded_parent = expanded[pid]
        spec = {
            "task_id": pid,
            "objective": top["title"],
            "acceptance": [top["acceptance"]],
            "depends_on": list(top["dependencies"]),
            "area": top["module"].lower(),
            "project_id": PROJECT_ID,
            "module": top["module"],
            "milestone": top["milestone"],
            "priority": top["priority"],
            "title": top["title"],
            "reuse_notes": top.get("reuse_notes", ""),
            "required_owner_gate": bool(top.get("required_owner_gate")),
            "manual_owner_gate_required": bool(expanded_parent.get("manual_owner_gate_required")),
            "execution_mode": expanded_parent.get("execution_mode", "worker"),
            "suggested_scope_roots": expanded_parent.get("suggested_scope_roots", []),
            "module_guardrails": expanded_parent.get("module_guardrails", []),
            "special_instructions": expanded_parent.get("special_instructions", []),
            "completion_rule": expanded_parent.get("completion_rule", ""),
            "source_parent": top,
            "expanded_parent": expanded_parent,
            "subtasks": list(children[pid]),
        }
        normalized.append({
            "task_id": pid,
            "module": top["module"],
            "milestone": top["milestone"],
            "priority": top["priority"],
            "owner_gate": bool(expanded_parent.get("manual_owner_gate_required") or top.get("required_owner_gate")),
            "dependencies": list(top["dependencies"]),
            "spec": spec,
            "payload_sha": payload_sha(spec),
            "children": list(children[pid]),
        })

    validation = {
        "parent_count": len(normalized),
        "subtask_count": sum(len(x["children"]) for x in normalized),
        "unique_parent_ids": len({x["task_id"] for x in normalized}),
        "unique_subtask_ids": len({c["id"] for x in normalized for c in x["children"]}),
        "dependency_edges": edge_count,
        "dependency_cycles": 0,
        "topological_order_count": len(topological),
        "module_count": len(entries),
        "module_counts": module_counts,
        "owner_gates": [x["task_id"] for x in normalized if x["owner_gate"]],
        "source_ref": source_ref,
        "source_commit": source_commit,
        "parent_plan_blob_sha": parent_blob,
        "subtask_index_sha256": hashlib.sha256(index_raw).hexdigest(),
        "business_module_active": False,
    }
    _require(set(validation["owner_gates"]) == set(OWNER_GATE_IDS),
             "owner gate set differs from the reviewed nine-task set")
    project = {
        "project_id": PROJECT_ID,
        "project_name": "JARVIS V2 Full Build",
        "source_repository": parent_doc.get("source_repository"),
        "integration_branch": "develop",
        "parent_task_count": EXPECTED_PARENT_COUNT,
        "subtask_count": EXPECTED_SUBTASK_COUNT,
        "workers": 5,
        "model": "gpt-5.6-luna",
        "reasoning": "medium",
        "architecture_modules": 10,
        "workstreams": list(EXPECTED_MODULES),
        "business_module_active": False,
        "source_ref": source_ref,
        "source_commit": source_commit,
        "parent_plan_blob_sha": parent_blob,
        "subtask_index_sha256": validation["subtask_index_sha256"],
        "module_hashes": module_hashes,
    }
    return FullPlan(project, tuple(normalized), children, parent_blob,
                    validation["subtask_index_sha256"], module_hashes, validation)
