"""Read-only, allowlisted GitHub source metadata and pinned-commit analysis."""
from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import re
from urllib.parse import urlsplit


MAX_QUERY_BYTES = 512
MAX_RESULTS = 50
MAX_FILES = 256
MAX_PATH_BYTES = 512
MAX_LICENSE_BYTES = 128
MAX_REPOSITORIES = 32
_PART = re.compile(r"^[A-Za-z0-9_.-]{1,100}$")
_LICENSE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.+-]{0,63}$")
_SHA = re.compile(r"^[0-9a-fA-F]{40}$")
_BLOCKED_PATH_PARTS = frozenset({
    ".git", ".env", ".aws", ".ssh", "secrets", "secret", "credentials",
    "private", "certificates", "tokens",
})


class GitHubSourceError(ValueError):
    """Raised when a GitHub source policy or result is malformed."""


def _text(value: object, label: str, maximum: int, *, empty: bool = False) -> str:
    if (
        not isinstance(value, str)
        or (not empty and not value.strip())
        or len(value.encode("utf-8")) > maximum
        or any(ord(char) < 32 for char in value)
    ):
        raise GitHubSourceError(f"invalid {label}")
    return value


def _sha(value: object) -> str:
    if not isinstance(value, str) or not _SHA.fullmatch(value):
        raise GitHubSourceError("invalid commit SHA")
    return value.lower()


def _timestamp(clock: Callable[[], datetime]) -> str:
    value = clock()
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise GitHubSourceError("clock must return a timezone-aware datetime")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _safe_path(path: object) -> str:
    path = _text(path, "source path", MAX_PATH_BYTES)
    parts = path.split("/")
    if path.startswith("/") or "\\" in path or any(part in {"", ".", ".."} for part in parts):
        raise GitHubSourceError("unsafe source path")
    if any(part.casefold() in _BLOCKED_PATH_PARTS for part in parts):
        raise GitHubSourceError("protected source path")
    return path


@dataclass(frozen=True)
class RepositoryPolicy:
    """One exact GitHub repository allowlist entry."""

    owner: str
    name: str
    allowed_licenses: tuple[str, ...]
    allowed_paths: tuple[str, ...] = ()
    access_scope: str = "public_read"

    def __post_init__(self) -> None:
        if not _PART.fullmatch(self.owner) or not _PART.fullmatch(self.name):
            raise GitHubSourceError("invalid repository identity")
        if not self.allowed_licenses or len(self.allowed_licenses) > 32:
            raise GitHubSourceError("license allowlist is empty or too large")
        licenses = tuple(_text(item, "license", MAX_LICENSE_BYTES) for item in self.allowed_licenses)
        if any(not _LICENSE.fullmatch(item) for item in licenses) or len(set(licenses)) != len(licenses):
            raise GitHubSourceError("invalid license allowlist")
        paths = tuple(_safe_path(item).rstrip("/") for item in self.allowed_paths)
        if len(paths) > 64:
            raise GitHubSourceError("path allowlist is too large")
        _text(self.access_scope, "access scope", 128)
        object.__setattr__(self, "allowed_licenses", licenses)
        object.__setattr__(self, "allowed_paths", paths)

    @property
    def repository(self) -> str:
        return f"{self.owner}/{self.name}"

    def allows_path(self, path: str) -> bool:
        return not self.allowed_paths or any(path == root or path.startswith(root + "/") for root in self.allowed_paths)


@dataclass(frozen=True)
class SourceFile:
    path: str
    blob_sha: str
    size: int
    executable: bool = False

    def __post_init__(self) -> None:
        _safe_path(self.path)
        _sha(self.blob_sha)
        if type(self.size) is not int or not 0 <= self.size <= 512 * 1024:
            raise GitHubSourceError("source file is outside the bounded range")
        if type(self.executable) is not bool:
            raise GitHubSourceError("invalid executable flag")

    def as_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "blob_sha": self.blob_sha.lower(),
            "size": self.size,
            "executable": self.executable,
        }


@dataclass(frozen=True)
class PinnedCommit:
    repository: str
    commit_sha: str
    license_id: str
    files: tuple[SourceFile, ...]
    source_date: str | None
    observed_at: str
    execution_allowed: bool = False

    def __post_init__(self) -> None:
        _text(self.repository, "repository", 201)
        _sha(self.commit_sha)
        _text(self.license_id, "license", MAX_LICENSE_BYTES)
        if len(self.files) > MAX_FILES or any(not isinstance(item, SourceFile) for item in self.files):
            raise GitHubSourceError("source file list is outside the bounded range")
        if self.source_date is not None:
            _text(self.source_date, "source date", 64)
        _text(self.observed_at, "observation timestamp", 64)
        if self.execution_allowed is not False:
            raise GitHubSourceError("repository code execution is disabled")

    def as_dict(self) -> dict[str, object]:
        return {
            "repository": self.repository,
            "commit_sha": self.commit_sha.lower(),
            "license_id": self.license_id,
            "files": [item.as_dict() for item in self.files],
            "source_date": self.source_date,
            "observed_at": self.observed_at,
            "execution_allowed": False,
        }


@dataclass(frozen=True)
class GitHubSearchHit:
    repository: str
    uri: str
    title: str
    description: str
    observed_at: str

    def __post_init__(self) -> None:
        _text(self.repository, "repository", 201)
        _text(self.uri, "repository URI", 512)
        _text(self.title, "title", 512, empty=True)
        _text(self.description, "description", 2048, empty=True)
        _text(self.observed_at, "observation timestamp", 64)

    def as_dict(self) -> dict[str, str]:
        return {
            "repository": self.repository,
            "uri": self.uri,
            "title": self.title,
            "description": self.description,
            "observed_at": self.observed_at,
        }


@dataclass(frozen=True)
class GitHubSearchResult:
    status: str
    observed_at: str
    results: tuple[GitHubSearchHit, ...] = ()
    failure: str | None = None

    def __post_init__(self) -> None:
        if self.status not in {"ok", "empty", "failed", "blocked"}:
            raise GitHubSourceError("invalid search status")
        _text(self.observed_at, "observation timestamp", 64)
        if len(self.results) > MAX_RESULTS or any(not isinstance(item, GitHubSearchHit) for item in self.results):
            raise GitHubSourceError("search results exceed the bounded range")
        if self.failure is not None:
            _text(self.failure, "failure", 128)

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "observed_at": self.observed_at,
            "results": [item.as_dict() for item in self.results],
            "failure": self.failure,
        }


@dataclass(frozen=True)
class GitHubCommitResult:
    status: str
    observed_at: str
    commit: PinnedCommit | None = None
    failure: str | None = None

    def __post_init__(self) -> None:
        if self.status not in {"ok", "empty", "failed", "blocked"}:
            raise GitHubSourceError("invalid commit status")
        _text(self.observed_at, "observation timestamp", 64)
        if self.commit is not None and not isinstance(self.commit, PinnedCommit):
            raise GitHubSourceError("invalid pinned commit")
        if self.failure is not None:
            _text(self.failure, "failure", 128)

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "observed_at": self.observed_at,
            "commit": None if self.commit is None else self.commit.as_dict(),
            "failure": self.failure,
        }


SearchTransport = Callable[[str, int], Iterable[Mapping[str, object]]]
CommitTransport = Callable[[str, str, RepositoryPolicy], Mapping[str, object]]


class GitHubSourceAdapter:
    """Analyze injected GitHub metadata without network access or code execution."""

    def __init__(
        self,
        repositories: Iterable[RepositoryPolicy],
        *,
        search_transport: SearchTransport | None = None,
        commit_transport: CommitTransport | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        policies = tuple(repositories)
        if not 1 <= len(policies) <= MAX_REPOSITORIES or any(
            not isinstance(item, RepositoryPolicy) for item in policies
        ):
            raise GitHubSourceError("repository allowlist is outside the bounded range")
        if len({item.repository for item in policies}) != len(policies):
            raise GitHubSourceError("duplicate repository allowlist entry")
        if search_transport is not None and not callable(search_transport):
            raise GitHubSourceError("search transport must be callable")
        if commit_transport is not None and not callable(commit_transport):
            raise GitHubSourceError("commit transport must be callable")
        if clock is not None and not callable(clock):
            raise GitHubSourceError("clock must be callable")
        self.repositories = {item.repository: item for item in policies}
        self.search_transport = search_transport
        self.commit_transport = commit_transport
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def search(self, query: str, *, limit: int = 10) -> GitHubSearchResult:
        query = _text(query, "query", MAX_QUERY_BYTES)
        if type(limit) is not int or not 1 <= limit <= MAX_RESULTS:
            raise GitHubSourceError("search limit is outside the bounded range")
        observed_at = _timestamp(self.clock)
        if self.search_transport is None:
            return GitHubSearchResult("failed", observed_at, failure="search_unavailable")
        hits: list[GitHubSearchHit] = []
        try:
            values = self.search_transport(query, limit)
            if isinstance(values, (str, bytes, Mapping)):
                raise GitHubSourceError("search transport returned an invalid collection")
            for item in values:
                if not isinstance(item, Mapping):
                    raise GitHubSourceError("search result is invalid")
                repository_value = item.get("repository")
                if not isinstance(repository_value, str):
                    continue
                repository = repository_value
                policy = self.repositories.get(repository)
                if policy is None:
                    continue
                uri_value = item.get("uri", f"https://github.com/{repository}")
                if not isinstance(uri_value, str):
                    continue
                uri = uri_value
                if not self._repository_uri(uri, repository):
                    continue
                title = item.get("title", "")
                description = item.get("description", "")
                if not isinstance(title, str) or not isinstance(description, str):
                    raise GitHubSourceError("search result metadata is incomplete")
                hits.append(GitHubSearchHit(repository, uri, title, description, observed_at))
                if len(hits) >= limit:
                    break
        except TimeoutError:
            return GitHubSearchResult("failed", observed_at, failure="provider_timeout")
        except (ConnectionError, OSError):
            return GitHubSearchResult("failed", observed_at, failure="provider_unavailable")
        except (GitHubSourceError, TypeError, ValueError):
            return GitHubSearchResult("failed", observed_at, failure="provider_invalid")
        return GitHubSearchResult("ok" if hits else "empty", observed_at, tuple(hits))

    def inspect_commit(self, repository: str, commit_sha: str) -> GitHubCommitResult:
        observed_at = _timestamp(self.clock)
        policy = self.repositories.get(repository)
        if policy is None:
            return GitHubCommitResult("blocked", observed_at, failure="repository_not_allowlisted")
        try:
            commit_sha = _sha(commit_sha)
        except GitHubSourceError:
            return GitHubCommitResult("blocked", observed_at, failure="commit_not_pinned")
        if self.commit_transport is None:
            return GitHubCommitResult("failed", observed_at, failure="commit_unavailable")
        try:
            payload = self.commit_transport(repository, commit_sha, policy)
            if not isinstance(payload, Mapping):
                raise GitHubSourceError("commit transport returned an invalid object")
            returned_sha = payload.get("commit_sha", commit_sha)
            if not isinstance(returned_sha, str) or returned_sha.lower() != commit_sha:
                return GitHubCommitResult("blocked", observed_at, failure="commit_not_pinned")
            if payload.get("execution_requested") or payload.get("command") or payload.get("commands"):
                return GitHubCommitResult("blocked", observed_at, failure="code_execution_disabled")
            license_id = payload.get("license_id", payload.get("license"))
            if not isinstance(license_id, str) or license_id not in policy.allowed_licenses:
                return GitHubCommitResult("blocked", observed_at, failure="license_not_allowlisted")
            try:
                files = self._files(payload.get("files", ()), policy)
            except GitHubSourceError as exc:
                if str(exc) in {"source path is not allowlisted", "unsafe source path", "protected source path"}:
                    return GitHubCommitResult("blocked", observed_at, failure="source_path_not_allowlisted")
                raise
            source_date_value = payload.get("source_date")
            if source_date_value is not None and not isinstance(source_date_value, str):
                raise GitHubSourceError("invalid source date")
            source_date = source_date_value
            if source_date is not None:
                _text(source_date, "source date", 64)
            commit = PinnedCommit(repository, commit_sha, license_id, files, source_date, observed_at)
            return GitHubCommitResult("ok", observed_at, commit=commit)
        except TimeoutError:
            return GitHubCommitResult("failed", observed_at, failure="provider_timeout")
        except (ConnectionError, OSError):
            return GitHubCommitResult("failed", observed_at, failure="provider_unavailable")
        except (GitHubSourceError, TypeError, ValueError):
            return GitHubCommitResult("failed", observed_at, failure="provider_invalid")

    analyze_commit = inspect_commit

    @staticmethod
    def _repository_uri(uri: object, repository: str) -> bool:
        if not isinstance(uri, str) or len(uri.encode("utf-8")) > 512:
            return False
        try:
            parsed = urlsplit(uri)
        except ValueError:
            return False
        return (
            parsed.scheme == "https"
            and parsed.hostname == "github.com"
            and parsed.username is None
            and parsed.password is None
            and parsed.fragment == ""
            and parsed.path.rstrip("/") == f"/{repository}"
        )

    @staticmethod
    def _files(value: object, policy: RepositoryPolicy) -> tuple[SourceFile, ...]:
        if isinstance(value, (str, bytes, Mapping)):
            raise GitHubSourceError("commit files are invalid")
        try:
            values = tuple(value)  # type: ignore[arg-type]
        except TypeError as exc:
            raise GitHubSourceError("commit files are invalid") from exc
        if len(values) > MAX_FILES:
            raise GitHubSourceError("commit file list is too large")
        files: list[SourceFile] = []
        for item in values:
            if not isinstance(item, Mapping):
                raise GitHubSourceError("commit file is invalid")
            path = _safe_path(item.get("path"))
            if not policy.allows_path(path):
                raise GitHubSourceError("source path is not allowlisted")
            mode = item.get("mode", "100644")
            if not isinstance(mode, str) or mode not in {"100644", "100755"}:
                raise GitHubSourceError("unsupported source entry")
            blob_sha = item.get("blob_sha")
            size = item.get("size")
            if not isinstance(blob_sha, str) or type(size) is not int:
                raise GitHubSourceError("source file metadata is incomplete")
            files.append(SourceFile(
                path,
                blob_sha,
                size,
                mode == "100755",
            ))
        if len({item.path for item in files}) != len(files):
            raise GitHubSourceError("duplicate source path")
        return tuple(files)


GitHubRepositoryPolicy = RepositoryPolicy
PinnedCommitAnalysis = GitHubCommitResult


__all__ = [
    "GitHubCommitResult",
    "GitHubRepositoryPolicy",
    "GitHubSearchHit",
    "GitHubSearchResult",
    "GitHubSourceAdapter",
    "GitHubSourceError",
    "MAX_FILES",
    "MAX_RESULTS",
    "PinnedCommit",
    "PinnedCommitAnalysis",
    "RepositoryPolicy",
    "SourceFile",
]
