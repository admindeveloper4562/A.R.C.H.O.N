from datetime import datetime, timezone
import unittest

from jarvis_v2.research import (
    GitHubSourceAdapter,
    GitHubSourceError,
    RepositoryPolicy,
)


COMMIT = "a" * 40
BLOB = "b" * 40
OBSERVED = datetime(2026, 11, 17, 2, 3, 4, tzinfo=timezone.utc)


class ResearchGitHubTests(unittest.TestCase):
    def policy(self):
        return RepositoryPolicy(
            "admindeveloper4562",
            "A.R.C.H.O.N",
            ("MIT",),
            allowed_paths=("src/jarvis_v2",),
        )

    def adapter(self, **kwargs):
        return GitHubSourceAdapter((self.policy(),), clock=lambda: OBSERVED, **kwargs)

    def test_pinned_commit_requires_allowlisted_license_and_preserves_pin(self):
        def inspect(repository, commit_sha, policy):
            self.assertEqual((repository, commit_sha, policy.repository),
                             ("admindeveloper4562/A.R.C.H.O.N", COMMIT, policy.repository))
            return {
                "commit_sha": COMMIT,
                "license_id": "MIT",
                "source_date": "2026-11-16T00:00:00Z",
                "files": [{
                    "path": "src/jarvis_v2/research/github.py",
                    "blob_sha": BLOB,
                    "size": 128,
                }],
            }

        result = self.adapter(commit_transport=inspect).inspect_commit(
            "admindeveloper4562/A.R.C.H.O.N", COMMIT
        )
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.commit.commit_sha, COMMIT)
        self.assertEqual(result.commit.license_id, "MIT")
        self.assertFalse(result.commit.execution_allowed)
        self.assertEqual(result.commit.files[0].blob_sha, BLOB)

    def test_repository_allowlist_blocks_before_transport(self):
        called = []

        def inspect(*_args):
            called.append(True)
            return {}

        result = self.adapter(commit_transport=inspect).inspect_commit("other/repo", COMMIT)
        self.assertEqual(result.failure, "repository_not_allowlisted")
        self.assertEqual(called, [])

    def test_license_and_execution_barriers_fail_closed(self):
        def unlicensed(*_args):
            return {"commit_sha": COMMIT, "license_id": "GPL-3.0-only"}

        result = self.adapter(commit_transport=unlicensed).inspect_commit(
            "admindeveloper4562/A.R.C.H.O.N", COMMIT
        )
        self.assertEqual((result.status, result.failure), ("blocked", "license_not_allowlisted"))

        def executable(*_args):
            return {"commit_sha": COMMIT, "license_id": "MIT", "commands": ["./setup.sh"]}

        result = self.adapter(commit_transport=executable).inspect_commit(
            "admindeveloper4562/A.R.C.H.O.N", COMMIT
        )
        self.assertEqual((result.status, result.failure), ("blocked", "code_execution_disabled"))

    def test_path_allowlist_and_pinned_sha_are_enforced(self):
        def unsafe(*_args):
            return {
                "commit_sha": COMMIT,
                "license_id": "MIT",
                "files": [{"path": "tests/test.py", "blob_sha": BLOB, "size": 1}],
            }

        result = self.adapter(commit_transport=unsafe).inspect_commit(
            "admindeveloper4562/A.R.C.H.O.N", COMMIT
        )
        self.assertEqual((result.status, result.failure), ("blocked", "source_path_not_allowlisted"))

        called = []

        def inspect(*_args):
            called.append(True)
            return {}

        result = self.adapter(commit_transport=inspect).inspect_commit(
            "admindeveloper4562/A.R.C.H.O.N", "not-a-commit"
        )
        self.assertEqual((result.status, result.failure), ("blocked", "commit_not_pinned"))
        self.assertEqual(called, [])

    def test_search_returns_only_allowlisted_exact_github_repositories(self):
        def search(query, limit):
            self.assertEqual((query, limit), ("archon", 5))
            return [
                {"repository": "other/repo", "title": "foreign"},
                {"repository": "admindeveloper4562/A.R.C.H.O.N", "title": "ARCHON"},
                {"repository": "admindeveloper4562/A.R.C.H.O.N", "uri": "https://evil.example/repo"},
            ]

        result = self.adapter(search_transport=search).search("archon", limit=5)
        self.assertEqual(result.status, "ok")
        self.assertEqual([item.repository for item in result.results], ["admindeveloper4562/A.R.C.H.O.N"])

    def test_missing_transport_and_provider_failures_are_bounded(self):
        result = self.adapter().inspect_commit("admindeveloper4562/A.R.C.H.O.N", COMMIT)
        self.assertEqual((result.status, result.failure), ("failed", "commit_unavailable"))

        def timeout(*_args):
            raise TimeoutError("provider internals")

        result = self.adapter(commit_transport=timeout).inspect_commit(
            "admindeveloper4562/A.R.C.H.O.N", COMMIT
        )
        self.assertEqual(result.failure, "provider_timeout")
        self.assertNotIn("provider internals", str(result.as_dict()))

    def test_policy_rejects_empty_license_allowlist(self):
        with self.assertRaisesRegex(GitHubSourceError, "license"):
            RepositoryPolicy("owner", "repo", ())


if __name__ == "__main__":
    unittest.main()
