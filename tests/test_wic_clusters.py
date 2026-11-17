from datetime import datetime, timezone
import tempfile
import unittest

from jarvis_v2.wic import (
    SourceObservation,
    StoryClusterStore,
    StoryClusterer,
    WICError,
    normalize_url,
)


def observation(observation_id, source_id, article_url):
    return SourceObservation(
        observation_id, source_id, f"https://{source_id}.example/feed", article_url,
        datetime(2026, 11, 17, 1, 2, 3, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
    )


class WICClusterTests(unittest.TestCase):
    def test_normalize_url_removes_tracking_and_fragment_variants(self):
        self.assertEqual(
            normalize_url("https://news.example/article/?utm_source=feed&b=2&fbclid=x&a=1"),
            "https://news.example/article?a=1&b=2",
        )

    def test_same_incident_keeps_both_sources_in_one_cluster(self):
        first = observation("obs-1", "alpha", "https://alpha.example/article/1")
        second = observation("obs-2", "beta", "https://beta.example/article/2")
        with tempfile.TemporaryDirectory() as directory:
            with StoryClusterStore(directory + "/wic.sqlite") as store:
                cluster = StoryClusterer(store).cluster(
                    (first, second), incident_key="event-2026-11-17-1"
                )
                self.assertEqual(cluster.source_ids, ("alpha", "beta"))
                self.assertEqual(cluster.observation_ids, ("obs-1", "obs-2"))
                self.assertEqual(cluster.article_urls, (first.article_url, second.article_url))
                self.assertNotEqual(cluster.article_urls[0], cluster.article_urls[1])

    def test_cluster_membership_survives_reopen_and_replay(self):
        first = observation("obs-1", "alpha", "https://alpha.example/article/1")
        with tempfile.TemporaryDirectory() as directory:
            path = directory + "/wic.sqlite"
            with StoryClusterStore(path) as store:
                clusterer = StoryClusterer(store)
                first_cluster = clusterer.cluster((first,), incident_key="event-1")
                replay = clusterer.cluster((first,), incident_key="event-1")
                self.assertEqual(replay, first_cluster)
            with StoryClusterStore(path) as store:
                self.assertEqual(store.get("incident:event-1"), first_cluster)

    def test_different_urls_require_explicit_incident_key(self):
        first = observation("obs-1", "alpha", "https://alpha.example/article/1")
        second = observation("obs-2", "beta", "https://beta.example/article/2")
        with tempfile.TemporaryDirectory() as directory:
            with StoryClusterStore(directory + "/wic.sqlite") as store:
                with self.assertRaisesRegex(WICError, "incident key"):
                    StoryClusterer(store).cluster((first, second))

    def test_one_observation_cannot_be_assigned_to_two_incidents(self):
        first = observation("obs-1", "alpha", "https://alpha.example/article/1")
        with tempfile.TemporaryDirectory() as directory:
            with StoryClusterStore(directory + "/wic.sqlite") as store:
                clusterer = StoryClusterer(store)
                clusterer.cluster((first,), incident_key="event-1")
                with self.assertRaisesRegex(WICError, "another cluster"):
                    clusterer.cluster((first,), incident_key="event-2")


if __name__ == "__main__":
    unittest.main()
