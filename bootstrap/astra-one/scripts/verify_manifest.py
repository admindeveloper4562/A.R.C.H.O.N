"""Verify the fixed Astra package tree against its source manifest."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath


class ManifestError(ValueError):
    """Raised when package contents or manifest paths are unsafe."""


GENERATED_PARTS = frozenset({
    "build", "dist", "node_modules", "__pycache__", ".pytest_cache", ".test-output", ".wrangler",
})
GENERATED_SUFFIXES = frozenset({".pyc", ".pyo"})
WINDOWS_RESERVED = frozenset({
    "con", "prn", "aux", "nul",
    *(f"com{index}" for index in range(1, 10)),
    *(f"lpt{index}" for index in range(1, 10)),
})


def _validate_windows_component(part: str) -> None:
    if (not part or part.endswith((".", " ")) or any(char in part for char in ':*?"<>|')):
        raise ManifestError("Windows-unsafe package path component")
    stem = part.split(".", 1)[0].casefold()
    if stem in WINDOWS_RESERVED:
        raise ManifestError("Windows-reserved package path component")


def _is_generated(relative: PurePosixPath) -> bool:
    return any(
        part.casefold() in GENERATED_PARTS
        or part.casefold().endswith(".egg-info")
        or PurePosixPath(part).suffix.casefold() in GENERATED_SUFFIXES
        for part in relative.parts
    )


def _safe_relative(name: object) -> PurePosixPath:
    if (not isinstance(name, str) or not name or "\\" in name or "\x00" in name
            or name.startswith("/") or name.endswith("/") or "//" in name):
        raise ManifestError("manifest path must be a non-empty POSIX relative path")
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise ManifestError("manifest path is absolute or contains traversal")
    for part in path.parts:
        _validate_windows_component(part)
    if _is_generated(path):
        raise ManifestError("generated artifact path is not allowed")
    if len(path.parts[0]) == 2 and path.parts[0][1] == ":":
        raise ManifestError("manifest path contains a drive prefix")
    return path


def _safe_path(root: Path, relative: PurePosixPath) -> Path:
    root = root.resolve()
    current = root
    for part in relative.parts:
        if current.is_symlink():
            raise ManifestError("symlink in package path")
        current = current / part
    if current.is_symlink():
        raise ManifestError("symlink in package path")
    try:
        if not current.resolve(strict=False).is_relative_to(root):
            raise ManifestError("package path escapes root")
    except AttributeError:
        if root not in current.resolve(strict=False).parents and current.resolve(strict=False) != root:
            raise ManifestError("package path escapes root")
    return current


def _inventory(root: Path) -> dict[tuple[str, ...], str]:
    """Return actual regular files, rejecting unsafe and generated entries."""
    found: dict[tuple[str, ...], str] = {}
    entries: dict[tuple[str, ...], str] = {}
    for current, directories, files in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        kept = []
        for name in directories:
            path = current_path / name
            relative = PurePosixPath(path.relative_to(root).as_posix())
            if path.is_symlink():
                raise ManifestError("symlink in package: " + relative.as_posix())
            if _is_generated(relative):
                raise ManifestError("generated artifact in package: " + relative.as_posix())
            key = tuple(part.casefold() for part in relative.parts)
            if key in entries:
                raise ManifestError("case-colliding package paths: " + entries[key] + " and " + relative.as_posix())
            entries[key] = relative.as_posix()
            kept.append(name)
        directories[:] = kept
        for name in files:
            path = current_path / name
            relative = PurePosixPath(path.relative_to(root).as_posix())
            for part in relative.parts:
                _validate_windows_component(part)
            if _is_generated(relative):
                raise ManifestError("generated artifact in package: " + relative.as_posix())
            if path.is_symlink() or not path.is_file():
                raise ManifestError("unsafe package entry: " + relative.as_posix())
            if relative.as_posix() == "MANIFEST.json":
                continue
            key = tuple(part.casefold() for part in relative.parts)
            if key in entries:
                raise ManifestError("case-colliding package paths: " + entries[key] + " and " + relative.as_posix())
            entries[key] = relative.as_posix()
            found[key] = relative.as_posix()
    return found


def _verify_manifest(root: Path) -> int:
    """Validate hashes, the complete file set, path safety and generated policy."""
    package_root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    if package_root.is_symlink() or not package_root.is_dir():
        raise ManifestError("package root must be a real directory")
    package_root = package_root.resolve()
    manifest_path = _safe_path(package_root, PurePosixPath("MANIFEST.json"))
    version_path = _safe_path(package_root, PurePosixPath("VERSION"))
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        version = version_path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ManifestError("invalid package metadata") from exc
    if not isinstance(manifest, dict) or manifest.get("version") != version:
        raise ManifestError("MANIFEST version mismatch")
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise ManifestError("manifest files must be a non-empty mapping")
    declared: dict[tuple[str, ...], str] = {}
    for name, digest in files.items():
        relative = _safe_relative(name)
        key = tuple(part.casefold() for part in relative.parts)
        if key in declared:
            raise ManifestError("case-colliding manifest paths: " + declared[key] + " and " + name)
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest.lower()):
            raise ManifestError("invalid SHA-256 for: " + name)
        path = _safe_path(package_root, relative)
        if not path.is_file() or path.is_symlink():
            raise ManifestError("manifest verification failed for: " + name)
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest.lower():
            raise ManifestError("manifest verification failed for: " + name)
        declared[key] = relative.as_posix()
    actual = _inventory(package_root)
    declared_names = set(declared.values())
    actual_names = set(actual.values())
    if declared_names != actual_names:
        raise ManifestError("MANIFEST file set mismatch")
    return len(files)


def verify_manifest() -> int:
    """Verify only the package containing this script."""
    return _verify_manifest(Path(__file__).resolve().parents[1])


def main() -> int:
    try:
        count = verify_manifest()
    except (ManifestError, OSError) as exc:
        print("MANIFEST verification failed: " + str(exc))
        return 1
    print("Astra One Linux release integrity OK:", count, "files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
