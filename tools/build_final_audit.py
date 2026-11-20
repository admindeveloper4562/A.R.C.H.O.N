#!/usr/bin/env python3
"""Build the final ARCHON source catalog and bounded local code index.

Python uses the stdlib AST. Other repository languages use small declaration
patterns and are reported as regex-parsed rather than AST-complete.
"""
from __future__ import annotations

import argparse
import ast
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Iterable
import json


CODE_LANGUAGES = {
    ".py": "python",
    ".js": "javascript",
    ".mjs": "javascript",
    ".ts": "typescript",
    ".sh": "shell",
    ".swift": "swift",
    ".sql": "sql",
}
INDEX_SUFFIXES = set(CODE_LANGUAGES) | {
    ".md",
    ".json",
    ".toml",
    ".yml",
    ".yaml",
    ".txt",
    ".service",
    ".timer",
    ".ps1",
    ".html",
    ".css",
    ".ini",
    ".cfg",
    ".conf",
    ".xml",
}
EXCLUDED_PARTS = {
    ".git",
    ".serena",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
}
SECURITY_WORDS = re.compile(
    r"\b(auth|authoriz|permission|scope|owner|approval|secret|token|password|"
    r"credential|sandbox|subprocess|command|path|filesystem|sql|rollback|"
    r"recovery|guardian|fence|stop|pause|rate.?limit)\b",
    re.IGNORECASE,
)
SIDE_EFFECT_PATTERNS = (
    ("filesystem", re.compile(r"\b(open|Path\(|write_text|write_bytes|unlink|rename|mkdir)\b")),
    ("database", re.compile(r"\b(sqlite3|connect\(|execute\(|commit\(|rollback\()\b")),
    ("subprocess", re.compile(r"\b(subprocess|Popen|run\(|check_call|systemd|git )\b")),
    ("network", re.compile(r"\b(requests|urllib|httpx|socket|fetch\(|curl )\b")),
    ("process", re.compile(r"\b(os\.environ|signal|thread|asyncio|sleep\()\b")),
)
BUILTIN_CALLS = {
    "Any", "Exception", "ValueError", "RuntimeError", "Path", "print", "len",
    "list", "dict", "set", "tuple", "str", "int", "float", "bool",
    "isinstance", "getattr", "hasattr", "sorted", "min", "max", "range",
    "enumerate", "zip", "open", "super",
}


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def relative(repo: Path, path: Path) -> str:
    return path.relative_to(repo).as_posix()


def excluded(repo: Path, path: Path) -> bool:
    rel = relative(repo, path)
    return (
        any(part in EXCLUDED_PARTS for part in path.relative_to(repo).parts)
        or path.name.startswith("codex-session-")
        or rel.startswith("docs/final-audit/evidence/")
    )


def iter_files(repo: Path, suffixes: set[str]) -> list[Path]:
    return sorted(
        path
        for path in repo.rglob("*")
        if path.is_file()
        and path.suffix.lower() in suffixes
        and not excluded(repo, path)
        and path.stat().st_size <= 2_000_000
    )


def module_name(rel: str) -> str:
    parts = list(Path(rel).with_suffix("").parts)
    for marker in ("src", "tools", "tests", "apps", "agents", "packages", "services", "infra"):
        if marker in parts:
            parts = parts[parts.index(marker) + 1 :]
            break
    if parts and parts[0] == "bootstrap":
        parts = parts[2:] if len(parts) > 2 and parts[1] == "astra-one" else parts[1:]
    if parts and parts[0] == "migration":
        parts = parts[1:]
    return ".".join(part.replace("-", "_") for part in parts) or rel.replace("/", ".")


def expr_name(node: ast.AST | None) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = expr_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def ast_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    result = f"{prefix} {node.name}({ast.unparse(node.args)})"
    if node.returns is not None:
        result += f" -> {ast.unparse(node.returns)}"
    return result


def body_text(source: str, node: ast.AST) -> str:
    start = getattr(node, "lineno", 1)
    end = getattr(node, "end_lineno", start)
    return "\n".join(source.splitlines()[start - 1 : end])


def side_effects(text: str) -> list[str]:
    return [label for label, pattern in SIDE_EFFECT_PATTERNS if pattern.search(text)]


def security_reasons(path: str, name: str, text: str) -> list[str]:
    reasons: list[str] = []
    if SECURITY_WORDS.search(f"{path} {name} {text}"):
        reasons.append("security or trust-boundary vocabulary")
    if re.search(r"\b(subprocess|os\.system|Popen|shell=True|eval\()", text):
        reasons.append("command or process execution")
    if re.search(r"\b(open|Path\(|write_text|unlink|rglob|glob\()", text):
        reasons.append("filesystem access")
    if re.search(r"\b(sqlite|execute\(|SELECT |INSERT |UPDATE |DELETE )", text, re.IGNORECASE):
        reasons.append("database or query access")
    if re.search(r"\b(requests|urllib|httpx|socket|fetch\()", text):
        reasons.append("external or network access")
    return sorted(set(reasons))


def maintenance_status(path: str) -> str:
    if path.startswith("migration/imported/"):
        return "legacy-imported"
    if path.startswith("bootstrap/astra-one/"):
        return "legacy-bootstrap"
    if path.startswith("tests/") or "/tests/" in path:
        return "test"
    return "active"


def recommendation(path: str, name: str) -> str:
    status = maintenance_status(path)
    if status == "legacy-imported":
        return "retain as provenance; replace only through reviewed native migration"
    if status == "legacy-bootstrap":
        return "retain until native SDA/Guardian cutover evidence is complete"
    if re.search(r"(wrapper|adapter|compat|legacy|alias)", f"{path} {name}", re.I):
        return "review callers, public contract, and security role before simplification"
    return "retain; no evidence-backed removal candidate from static analysis alone"


def make_record(
    *,
    path: str,
    module: str,
    symbol: str,
    qualified_name: str,
    kind: str,
    start: int,
    end: int,
    signature: str,
    purpose: str,
    inputs: list[str],
    outputs: list[str],
    body: str,
    dependencies: list[str],
    called_raw: list[str],
) -> dict[str, Any]:
    return {
        "module": module,
        "file_path": path,
        "line_range": [start, end],
        "symbol_name": symbol,
        "qualified_name": qualified_name,
        "kind": kind,
        "signature": signature,
        "purpose": purpose or "undocumented",
        "inputs": inputs,
        "outputs": outputs,
        "side_effects": side_effects(body),
        "dependencies": dependencies,
        "callers": [],
        "called_functions": [],
        "called_symbols_raw": sorted(set(called_raw)),
        "exceptions_and_failure_behavior": [],
        "authentication_or_permission_requirements": sorted(
            {match.group(0).lower() for match in SECURITY_WORDS.finditer(f"{path} {symbol} {body}")}
        ),
        "security_implications": security_reasons(path, symbol, body),
        "existing_test_coverage": [],
        "known_defects": [marker for marker in ("TODO", "FIXME", "XXX") if marker in body],
        "refactoring_recommendation": recommendation(path, symbol),
        "maintenance_status": maintenance_status(path),
        "_body": body,
    }


def parse_python(repo: Path, path: Path) -> tuple[list[dict[str, Any]], list[str], str | None]:
    rel = relative(repo, path)
    source = read_text(path)
    try:
        tree = ast.parse(source, filename=rel)
    except SyntaxError as exc:
        return [], [], f"{exc.msg} at line {exc.lineno}"
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append("." * node.level + (node.module or ""))
    records: list[dict[str, Any]] = []
    module = module_name(rel)

    def visit(node: ast.AST, prefix: str = "", parent: str = "") -> None:
        if isinstance(node, ast.ClassDef):
            name = f"{prefix}.{node.name}" if prefix else node.name
            body = body_text(source, node)
            records.append(
                make_record(
                    path=rel,
                    module=module,
                    symbol=node.name,
                    qualified_name=f"{module}.{name}",
                    kind="class",
                    start=node.lineno,
                    end=getattr(node, "end_lineno", node.lineno),
                    signature=f"class {node.name}({', '.join(ast.unparse(base) for base in node.bases)})",
                    purpose=ast.get_docstring(node) or "",
                    inputs=[ast.unparse(base) for base in node.bases],
                    outputs=["class instance"],
                    body=body,
                    dependencies=sorted(set(imports)),
                    called_raw=[],
                )
            )
            for child in node.body:
                if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    visit(child, name, "class")
            return
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = f"{prefix}.{node.name}" if prefix else node.name
            body = body_text(source, node)
            called = [
                expr_name(child.func)
                for child in ast.walk(node)
                if isinstance(child, ast.Call) and expr_name(child.func)
            ]
            raises: list[str] = []
            for child in ast.walk(node):
                if isinstance(child, ast.Raise) and child.exc is not None:
                    raises.append(expr_name(child.exc) or ast.unparse(child.exc))
                elif isinstance(child, ast.ExceptHandler):
                    raises.append(expr_name(child.type) or (ast.unparse(child.type) if child.type else "bare except"))
            args = [
                arg.arg
                for arg in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)
                if arg.arg not in {"self", "cls"}
            ]
            if node.args.vararg:
                args.append("*" + node.args.vararg.arg)
            if node.args.kwarg:
                args.append("**" + node.args.kwarg.arg)
            returns = [ast.unparse(node.returns)] if node.returns is not None else []
            return_count = sum(isinstance(child, ast.Return) for child in ast.walk(node))
            if return_count and not returns:
                returns = [f"return statements: {return_count}"]
            record = make_record(
                path=rel,
                module=module,
                symbol=node.name,
                qualified_name=f"{module}.{name}",
                kind="method" if parent == "class" else "function",
                start=node.lineno,
                end=getattr(node, "end_lineno", node.lineno),
                signature=ast_signature(node),
                purpose=ast.get_docstring(node) or "",
                inputs=args,
                outputs=returns,
                body=body,
                dependencies=sorted(set(imports)),
                called_raw=called,
            )
            record["exceptions_and_failure_behavior"] = sorted(set(raises))
            if len(node.body) == 1 and isinstance(node.body[0], ast.Return) and isinstance(node.body[0].value, ast.Call):
                record["wrapper_candidate"] = True
            records.append(record)
            for child in node.body:
                if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    visit(child, name, "function")

    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            visit(node)
    return records, sorted(set(imports)), None


def parse_other(repo: Path, path: Path) -> tuple[list[dict[str, Any]], list[str], str | None]:
    rel = relative(repo, path)
    source = read_text(path)
    language = CODE_LANGUAGES[path.suffix.lower()]
    patterns: list[tuple[re.Pattern[str], str]] = []
    if language in {"javascript", "typescript"}:
        patterns = [
            (re.compile(r"\b(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(([^)]*)\)"), "function"),
            (re.compile(r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>"), "function"),
        ]
    elif language == "shell":
        patterns = [(re.compile(r"^\s*(?:function\s+)?([A-Za-z_]\w*)\s*\(\)\s*\{"), "function")]
    elif language == "swift":
        patterns = [(re.compile(r"^\s*(?:[\w]+\s+)*func\s+([A-Za-z_]\w*)\s*\(([^)]*)\)"), "function")]
    elif language == "sql":
        patterns = [(re.compile(r"\bCREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+([A-Za-z_]\w*)", re.I), "function")]
    records: list[dict[str, Any]] = []
    module = module_name(rel)
    for line_number, line in enumerate(source.splitlines(), 1):
        for pattern, kind in patterns:
            match = pattern.search(line)
            if not match:
                continue
            name = match.group(1)
            args = [item.strip() for item in match.group(2).split(",") if item.strip()] if match.lastindex and match.lastindex >= 2 else []
            records.append(
                make_record(
                    path=rel,
                    module=module,
                    symbol=name,
                    qualified_name=f"{module}.{name}",
                    kind=kind,
                    start=line_number,
                    end=line_number,
                    signature=line.strip(),
                    purpose="regex-parsed declaration",
                    inputs=args,
                    outputs=[],
                    body=line,
                    dependencies=[],
                    called_raw=[],
                )
            )
            break
    return records, [], None


def parse_code(repo: Path, paths: Iterable[Path]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records: list[dict[str, Any]] = []
    parse_errors: list[dict[str, str]] = []
    language_files: defaultdict[str, int] = defaultdict(int)
    file_metadata: list[dict[str, Any]] = []
    for path in paths:
        rel = relative(repo, path)
        language = CODE_LANGUAGES[path.suffix.lower()]
        language_files[language] += 1
        source_bytes = path.read_bytes()
        file_metadata.append(
            {
                "path": rel,
                "language": language,
                "size_bytes": len(source_bytes),
                "content_sha256": sha256(source_bytes),
                "git_blob_sha": git(repo, "hash-object", "--", rel),
            }
        )
        found, _, error = (
            parse_python(repo, path)
            if language == "python"
            else parse_other(repo, path)
        )
        records.extend(found)
        if error:
            parse_errors.append({"path": rel, "error": error})
    return records, {
        "source_files": len(file_metadata),
        "language_files": dict(sorted(language_files.items())),
        "files": file_metadata,
        "parse_errors": parse_errors,
    }


def resolve_relations(records: list[dict[str, Any]], all_text: dict[str, str]) -> dict[str, Any]:
    by_name: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    by_module_name: defaultdict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_name[record["symbol_name"]].append(record)
        by_module_name[(record["module"], record["symbol_name"])].append(record)
    unresolved: list[dict[str, str]] = []
    for record in records:
        targets: set[str] = set()
        for raw in record.pop("called_symbols_raw", []):
            leaf = raw.rsplit(".", 1)[-1]
            candidates = by_module_name.get((record["module"], leaf), [])
            if not candidates:
                candidates = by_name.get(leaf, [])
            if len(candidates) == 1:
                targets.add(candidates[0]["qualified_name"])
                candidates[0]["callers"].append(record["qualified_name"])
            elif not candidates and leaf not in BUILTIN_CALLS:
                unresolved.append({"caller": record["qualified_name"], "symbol": raw})
        record["called_functions"] = sorted(targets)
        record["callers"] = sorted(set(record["callers"]))
    for record in records:
        record["existing_test_coverage"] = sorted(
            path
            for path, text in all_text.items()
            if (path.startswith("tests/") or "/tests/" in path)
            and re.search(r"\b" + re.escape(record["symbol_name"]) + r"\b", text)
        )
    for record in records:
        record.pop("_body", None)
    dead = [
        record
        for record in records
        if not record["callers"]
        and record["kind"] in {"function", "method", "class"}
        and not record["symbol_name"].startswith("__")
        and record["symbol_name"] not in {"main"}
    ]
    return {
        "unresolved_symbol_references": len(unresolved),
        "unresolved_examples": unresolved[:200],
        "suspected_dead_code_paths": len(dead),
        "dead_symbols": [
            {
                "qualified_name": record["qualified_name"],
                "file_path": record["file_path"],
                "line_range": record["line_range"],
                "kind": record["kind"],
            }
            for record in dead[:500]
        ],
    }


def markdown_table(rows: list[list[str]]) -> str:
    if not rows:
        return "_none_\n"
    width = len(rows[0])
    header = "| " + " | ".join(rows[0]) + " |"
    rule = "| " + " | ".join("---" for _ in range(width)) + " |"
    body = "\n".join("| " + " | ".join(row) + " |" for row in rows[1:])
    return "\n".join([header, rule, body, ""])


def md_code(value: object) -> str:
    return chr(96) + str(value) + chr(96)


def build_call_graph(symbols: list[dict[str, Any]]) -> str:
    rows = [["Caller", "Callee"]]
    for record in symbols:
        for target in record["called_functions"]:
            rows.append([md_code(record["qualified_name"]), md_code(target)])
    return (
        "# ARCHON Call Graph\n\n"
        "Static resolved edges only; unresolved and dynamic dispatch are counted in the catalog.\n\n"
        + markdown_table(rows[:5001])
    )


def build_module_dependencies(symbols: list[dict[str, Any]]) -> str:
    dependencies: defaultdict[str, set[str]] = defaultdict(set)
    for record in symbols:
        for dep in record["dependencies"]:
            dependencies[record["module"]].add(dep)
    rows = [["Module", "Observed imports"]]
    for module in sorted(dependencies):
        rows.append([
            md_code(module),
            ", ".join(md_code(dep) for dep in sorted(dependencies[module])) or "_none_",
        ])
    return "# ARCHON Module Dependencies\n\n" + markdown_table(rows)


def build_unused(catalog: dict[str, Any]) -> str:
    rows = [["Qualified name", "Location", "Kind"]]
    for item in catalog["relations"]["dead_symbols"]:
        rows.append([
            md_code(item["qualified_name"]),
            md_code(f"{item['file_path']}:{item['line_range'][0]}"),
            item["kind"],
        ])
    return (
        "# Suspected Unused Symbols\n\n"
        "Heuristic only: public APIs, CLI entry points, reflection, decorators, and external callers "
        "can make a symbol appear unused.\n\n"
        + markdown_table(rows)
    )


def build_security(symbols: list[dict[str, Any]]) -> str:
    rows = [["Qualified name", "Location", "Security implications"]]
    for record in symbols:
        if record["security_implications"]:
            rows.append([
                md_code(record["qualified_name"]),
                md_code(f"{record['file_path']}:{record['line_range'][0]}"),
                "; ".join(record["security_implications"]),
            ])
    return "# Security-Sensitive Functions\n\n" + markdown_table(rows)


def build_markdown(catalog: dict[str, Any]) -> dict[str, str]:
    coverage = catalog["coverage"]
    header = (
        "# ARCHON Function Catalog\n\n"
        f"Generated {md_code(catalog['generated_at'])} from base commit {md_code(catalog['source_sha'])}; "
        f"audited working tree state: {md_code(catalog['source_state'])}.\n\n"
        "Static inventory; callers, unresolved references, test links, and dead-code candidates "
        "are heuristic and must not be treated as acceptance receipts.\n\n"
        "## Coverage\n\n"
        + markdown_table([
            ["Metric", "Value"],
            ["Source files", str(coverage["source_files"])],
            ["Indexed files", str(coverage["indexed_files"])],
            ["Functions", str(coverage["functions"])],
            ["Methods", str(coverage["methods"])],
            ["Classes", str(coverage["classes"])],
            ["Parser errors", str(coverage["parser_errors"])],
            ["Unresolved symbols", str(coverage["unresolved_symbols"])],
            ["Untested functions/methods", str(coverage["untested_functions"])],
            ["Suspected dead paths", str(coverage["suspected_dead_code_paths"])],
        ])
        + "\n"
        "Supported parsing is AST-based for Python and declaration-pattern based for JavaScript, "
        "TypeScript, shell, Swift, and SQL. Unsupported constructs are explicitly counted as gaps.\n\n"
        "## Symbols\n\n"
    )
    rows = [["Qualified name", "Kind", "Location", "Signature", "Tests", "Status"]]
    for record in catalog["symbols"]:
        rows.append([
            md_code(record["qualified_name"]),
            record["kind"],
            md_code(f"{record['file_path']}:{record['line_range'][0]}-{record['line_range'][1]}"),
            record["signature"].replace("|", "\\|")[:180],
            str(len(record["existing_test_coverage"])),
            record["maintenance_status"],
        ])
    return {
        "FUNCTION_CATALOG.md": header + markdown_table(rows),
        "CALL_GRAPH.md": build_call_graph(catalog["symbols"]),
        "MODULE_DEPENDENCIES.md": build_module_dependencies(catalog["symbols"]),
        "UNUSED_SYMBOLS.md": build_unused(catalog),
        "SECURITY_SENSITIVE_FUNCTIONS.md": build_security(catalog["symbols"]),
    }


def index_files(repo: Path, paths: list[Path], source_sha: str, database: Path) -> dict[str, Any]:
    sys.path.insert(0, str(repo / "src"))
    try:
        from jarvis_v2.backend.code_index import RepositoryIndex
    except Exception as exc:
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}
    database.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(database.parent, 0o700)
    indexed = excluded_count = skipped = 0
    validations: dict[str, int] = {}
    try:
        with RepositoryIndex(database) as index:
            for path in paths:
                try:
                    content = read_text(path)
                except OSError:
                    skipped += 1
                    continue
                result = index.index_file(
                    relative(repo, path),
                    content,
                    blob_sha=git(repo, "hash-object", "--", relative(repo, path)),
                    source_sha=source_sha,
                )
                if result["excluded"]:
                    excluded_count += 1
                else:
                    indexed += 1
            for query in ("task queue", "rollback integrity", "module permission", "model gateway"):
                validations[query] = len(index.search(query, limit=5))
    except Exception as exc:
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}
    os.chmod(database, 0o600)
    return {
        "available": True,
        "database": str(database),
        "indexed": indexed,
        "excluded_sensitive": excluded_count,
        "skipped": skipped,
        "validation_result_counts": validations,
    }


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--index-db",
        type=Path,
        default=Path.home() / ".local/state/archon/code_index.sqlite3",
    )
    parser.add_argument("--no-index", action="store_true")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args(argv)
    repo = args.repo.resolve()
    output = repo / "docs" / "codebase"
    output.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat()
    source_sha = git(repo, "rev-parse", "HEAD")
    status_entries = len(git(repo, "status", "--porcelain").splitlines())
    code_paths = iter_files(repo, set(CODE_LANGUAGES))
    all_index_paths = iter_files(repo, INDEX_SUFFIXES)
    index_paths = [path for path in all_index_paths if path.stat().st_size <= 512 * 1024]
    index_oversize = [
        {"path": relative(repo, path), "size_bytes": path.stat().st_size}
        for path in all_index_paths
        if path.stat().st_size > 512 * 1024
    ]
    all_text = {relative(repo, path): read_text(path) for path in index_paths}
    symbols, file_data = parse_code(repo, code_paths)
    relations = resolve_relations(symbols, all_text)
    tested = sum(
        bool(record["existing_test_coverage"])
        for record in symbols
        if record["kind"] in {"function", "method"}
    )
    functions = sum(record["kind"] == "function" for record in symbols)
    methods = sum(record["kind"] == "method" for record in symbols)
    classes = sum(record["kind"] == "class" for record in symbols)
    catalog = {
        "schema_version": 1,
        "generated_at": generated_at,
        "source_sha": source_sha,
        "source_state": f"catalog generated from checkout {source_sha}; status snapshot had {status_entries} entries before output generation",
        "parser": {
            "python": "stdlib ast",
            "javascript": "declaration regex",
            "typescript": "declaration regex",
            "shell": "function regex",
            "swift": "function regex",
            "sql": "CREATE FUNCTION regex",
        },
        "coverage": {
            "source_files": file_data["source_files"],
            "indexed_files": len(index_paths),
            "functions": functions,
            "methods": methods,
            "classes": classes,
            "parser_errors": len(file_data["parse_errors"]),
            "unresolved_symbols": relations["unresolved_symbol_references"],
            "untested_functions": functions + methods - tested,
            "suspected_dead_code_paths": relations["suspected_dead_code_paths"],
            "language_files": file_data["language_files"],
        },
        "files": file_data["files"],
        "parse_errors": file_data["parse_errors"],
        "relations": relations,
        "symbols": symbols,
    }
    for name, content in build_markdown(catalog).items():
        (output / name).write_text(content, encoding="utf-8")
    write_json(output / "FUNCTION_CATALOG.json", catalog)
    index_result = (
        {"available": False, "skipped_by_flag": True}
        if args.no_index
        else index_files(repo, index_paths, source_sha, args.index_db.expanduser())
    )
    index_result["skipped_oversize"] = index_oversize
    write_json(output / "INDEX_VALIDATION.json", index_result)
    if args.self_check:
        assert source_sha and len(source_sha) == 40
        assert file_data["source_files"] > 0
        assert symbols
        assert (output / "FUNCTION_CATALOG.json").is_file()
        assert index_result.get("skipped_by_flag") or index_result.get("available")
    print(json.dumps({
        "source_sha": source_sha,
        "source_files": file_data["source_files"],
        "indexed_files": len(index_paths),
        "symbols": len(symbols),
        "functions": functions,
        "methods": methods,
        "classes": classes,
        "parser_errors": len(file_data["parse_errors"]),
        "index": index_result,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
