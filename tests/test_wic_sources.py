from datetime import datetime, timezone
import tempfile
import unittest

from jarvis_v2.wic import (
    IngestionResult,
    PublicSourceIngestion,
    SourceObservation,
    SourceHealth,
    SourcePolicy,
    SourceStore,
    WICError,
)


FETCHED = datetime(2026, 11, 17, 1, 2, 3, tzinfo=timezone.utc)


class WICSourceTests(unittest.TestCase):
    def policy(self):
        return SourcePolicy("news", "news.example", "public_metadata")

    def service(self, store, **kwargs):
        return PublicSourceIngestion(store, (self.policy(),), clock=lambda: FETCHED, **kwargs)

    def test_ingestion_retains_authorized_urls_and_separate_timestamps(self):
        with tempfile.TemporaryDirectory() as directory:
            with SourceStore(directory + "/wic.sqlite") as store:
                def feed(url, source, timeout):
                    self.assertEqual((url, source.source_id, timeout),
                                     ("https://news.example/feed", "news", 10))
                    return [{
                        "article_url": "https://news.example/article/1",
                        "title": "ARCHON update",
                        "published_at": "2026-11-16T00:00:00+07:00",
                        "updated_at": "2026-11-16T02:00:00Z",
                    }]

                result = self.service(store, feed_transport=feed).ingest(
                    "news", "https://news.example/feed"
                )
                self.assertIsInstance(result, IngestionResult)
                self.assertEqual(result.status, "ok")
                observation = result.observations[0]
                self.assertEqual(observation.feed_url, "https://news.example/feed")
                self.assertEqual(observation.article_url, "https://news.example/article/1")
                self.assertEqual(observation.fetched_at, "2026-11-17T01:02:03.000000Z")
                self.assertEqual(observation.published_at, "2026-11-15T17:00:00.000000Z")
                self.assertEqual(observation.source_updated_at, "2026-11-16T02:00:00.000000Z")
                self.assertEqual(store.latest(observation.article_url), observation)

    def test_observations_survive_store_reopen(self):
        with tempfile.TemporaryDirectory() as directory:
            path = directory + "/wic.sqlite"
            with SourceStore(path) as store:
                observation = SourceObservation(
                    "observation-1", "news", "https://news.example/feed",
                    "https://news.example/article/1", "2026-11-17T01:02:03Z",
                )
                self.assertTrue(store.save(observation))
            with SourceStore(path) as store:
                self.assertEqual(store.observations(), (observation,))

    def test_replay_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            with SourceStore(directory + "/wic.sqlite") as store:
                observation = SourceObservation(
                    "observation-1", "news", "https://news.example/feed",
                    "https://news.example/article/1", "2026-11-17T01:02:03Z",
                )
                self.assertTrue(store.save(observation))
                self.assertFalse(store.save(observation))
                self.assertEqual(len(store.observations()), 1)

    def test_foreign_items_are_rejected_without_persistence(self):
        with tempfile.TemporaryDirectory() as directory:
            with SourceStore(directory + "/wic.sqlite") as store:
                result = self.service(store, feed_transport=lambda *_: [
                    {"article_url": "https://other.example/article"},
                    {"article_url": "https://news.example/article/ok"},
                ]).ingest("news", "https://news.example/feed")
                self.assertEqual(result.status, "partial")
                self.assertEqual(result.rejected_items, 1)
                self.assertEqual(len(store.observations()), 1)

    def test_unallowlisted_feed_is_blocked_before_transport(self):
        called = []
        with tempfile.TemporaryDirectory() as directory:
            with SourceStore(directory + "/wic.sqlite") as store:
                result = self.service(store, feed_transport=lambda *_: called.append(True)).ingest(
                    "news", "https://other.example/feed"
                )
                self.assertEqual(result.status, "blocked")
                self.assertEqual(result.failure, "source_not_allowlisted")
                self.assertEqual(called, [])

    def test_provider_failure_is_bounded(self):
        with tempfile.TemporaryDirectory() as directory:
            with SourceStore(directory + "/wic.sqlite") as store:
                result = self.service(store, feed_transport=lambda *_: (_ for _ in ()).throw(
                    TimeoutError("provider internals")
                )).ingest("news", "https://news.example/feed")
                self.assertEqual(result.status, "failed")
                self.assertEqual(result.failure, "provider_timeout")
                self.assertNotIn("provider internals", str(result.as_dict()))

    def test_health_becomes_stale_after_successful_snapshot_age(self):
        with tempfile.TemporaryDirectory() as directory:
            with SourceStore(directory + "/wic.sqlite") as store:
                self.service(store, feed_transport=lambda *_: [
                    {"article_url": "https://news.example/article/1", "title": "Dated"}
                ]).ingest("news", "https://news.example/feed")
                fresh = store.health(
                    "news", now="2026-11-17T01:30:00Z", stale_after_seconds=3600
                )
                stale = store.health(
                    "news", now="2026-11-17T02:02:04Z", stale_after_seconds=3600
                )
                self.assertIsInstance(fresh, SourceHealth)
                self.assertEqual(fresh.status, "fresh")
                self.assertEqual(stale.status, "stale")
                self.assertEqual(stale.last_success_at, "2026-11-17T01:02:03.000000Z")

    def test_provider_outage_preserves_last_success_and_marks_outage(self):
        with tempfile.TemporaryDirectory() as directory:
            with SourceStore(directory + "/wic.sqlite") as store:
                self.service(store, feed_transport=lambda *_: [
                    {"article_url": "https://news.example/article/1", "title": "Dated"}
                ]).ingest("news", "https://news.example/feed")
                outage = PublicSourceIngestion(
                    store, (self.policy(),),
                    feed_transport=lambda *_: (_ for _ in ()).throw(TimeoutError("provider")),
                    clock=lambda: datetime(2026, 11, 17, 3, 2, 3, tzinfo=timezone.utc),
                ).ingest("news", "https://news.example/feed")
                health = store.health("news", now="2026-11-17T03:02:04Z")
                self.assertEqual((outage.status, outage.failure), ("failed", "provider_timeout"))
                self.assertEqual(health.status, "outage")
                self.assertEqual(health.failure, "provider_timeout")
                self.assertEqual(health.last_success_at, "2026-11-17T01:02:03.000000Z")
                self.assertEqual(len(store.observations()), 1)

    def test_unknown_health_has_no_false_timestamp(self):
        with tempfile.TemporaryDirectory() as directory:
            with SourceStore(directory + "/wic.sqlite") as store:
                health = store.health("news", now="2026-11-17T03:02:04Z")
                self.assertEqual(health.as_dict(), {
                    "source_id": "news", "status": "unknown",
                    "last_attempt_at": None, "last_success_at": None, "failure": None,
                })

    def test_invalid_dates_are_rejected_and_valid_items_remain(self):
        with tempfile.TemporaryDirectory() as directory:
            with SourceStore(directory + "/wic.sqlite") as store:
                result = self.service(store, feed_transport=lambda *_: [
                    {"article_url": "https://news.example/bad", "published_at": "not-a-date"},
                    {"article_url": "https://news.example/good", "published_at": "2026-11-16T00:00:00Z"},
                ]).ingest("news", "https://news.example/feed")
                self.assertEqual(result.status, "partial")
                self.assertEqual(result.rejected_items, 1)
                self.assertEqual([item.article_url for item in result.observations],
                                 ["https://news.example/good"])

    def test_non_public_policy_and_bad_observation_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            with SourceStore(directory + "/wic.sqlite") as store:
                with self.assertRaisesRegex(WICError, "not public"):
                    PublicSourceIngestion(
                        store, (SourcePolicy("private", "private.example", "scoped_private"),)
                    )
                with self.assertRaisesRegex(WICError, "article URL"):
                    SourceObservation(
                        "observation-1", "news", "https://news.example/feed",
                        "http://news.example/article", "2026-11-17T01:02:03Z",
                    )


if __name__ == "__main__":
    unittest.main()
