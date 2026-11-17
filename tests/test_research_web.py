from datetime import datetime, timezone
import hashlib
import unittest

from jarvis_v2.research import (
    ResearchError,
    SourcePolicy,
    WebDiscoveryService,
)


OBSERVED = datetime(2026, 11, 17, 1, 2, 3, tzinfo=timezone.utc)


class ResearchWebTests(unittest.TestCase):
    def policy(self):
        return SourcePolicy("docs", "docs.example", "public_metadata")

    def service(self, **kwargs):
        return WebDiscoveryService((self.policy(),), clock=lambda: OBSERVED, **kwargs)

    def test_search_preserves_source_and_observation_dates(self):
        def search(query, source, limit):
            self.assertEqual((query, source.source_id, limit), ("archon", "docs", 5))
            return [{
                "uri": "https://docs.example/archon",
                "title": "ARCHON",
                "snippet": "source result",
                "citation": "docs#archon",
                "source_date": "2026-11-16T00:00:00Z",
            }]

        result = self.service(search_transport=search).search("archon", limit=5)
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.results[0].source_date, "2026-11-16T00:00:00Z")
        self.assertEqual(result.results[0].observed_at, "2026-11-17T01:02:03.000000Z")

    def test_fetch_is_bounded_and_hashes_content(self):
        def fetch(uri, source, timeout):
            self.assertEqual((uri, source.source_id, timeout), ("https://docs.example/page", "docs", 10))
            return {
                "title": "Page", "content": "verified\ntext", "citation": "docs#page",
                "source_date": "2026-11-16T00:00:00Z",
            }

        result = self.service(fetch_transport=fetch).fetch("docs", "https://docs.example/page")
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.document.content_sha256, hashlib.sha256(b"verified\ntext").hexdigest())
        self.assertNotEqual(result.document.source_date, result.document.observed_at)

    def test_unallowlisted_source_is_blocked_before_transport(self):
        called = []

        def fetch(*_args):
            called.append(True)
            return {}

        result = self.service(fetch_transport=fetch).fetch("docs", "https://other.example/page")
        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.failure, "source_not_allowlisted")
        self.assertEqual(called, [])

    def test_foreign_search_results_are_not_returned(self):
        def search(*_args):
            return [{
                "uri": "https://other.example/page", "title": "foreign",
                "snippet": "no", "citation": "foreign#1",
            }]

        result = self.service(search_transport=search).search("query")
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.failure, "source_not_allowlisted")
        self.assertEqual(result.results, ())

    def test_provider_failures_are_explicit_and_redacted(self):
        def timeout(*_args):
            raise TimeoutError("provider internals")

        result = self.service(fetch_transport=timeout).fetch("docs", "https://docs.example/page")
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.failure, "provider_timeout")
        self.assertNotIn("provider internals", str(result.as_dict()))

        unavailable = self.service().fetch("docs", "https://docs.example/page")
        self.assertEqual(unavailable.failure, "fetch_unavailable")

    def test_invalid_content_and_requests_fail_closed(self):
        with self.assertRaisesRegex(ResearchError, "query"):
            self.service().search("\n")
        with self.assertRaisesRegex(ResearchError, "limit"):
            self.service().search("query", limit=0)

        def invalid(*_args):
            return {"title": "bad", "content": "", "citation": "docs#empty"}

        result = self.service(fetch_transport=invalid).fetch("docs", "https://docs.example/page")
        self.assertEqual(result.status, "empty")
        self.assertEqual(result.failure, "empty_response")

    def test_source_policy_rejects_non_https_and_userinfo(self):
        policy = self.policy()
        self.assertFalse(policy.allows("http://docs.example/page"))
        self.assertFalse(policy.allows("https://user:pass@docs.example/page"))
        self.assertTrue(policy.allows("https://docs.example/page"))


if __name__ == "__main__":
    unittest.main()
