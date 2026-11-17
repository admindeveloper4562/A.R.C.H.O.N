from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest

from jarvis_v2.research import (
    VideoResearchStore,
    YouTubeResearchService,
    video_id_from_url,
)


OBSERVED = datetime(2026, 11, 17, 1, 2, 3, tzinfo=timezone.utc)
URL = "https://www.youtube.com/watch?v=abc123"


class ResearchYouTubeTests(unittest.TestCase):
    def store(self, directory):
        return VideoResearchStore(Path(directory) / "research.sqlite")

    def test_metadata_offsets_source_links_and_record_persist(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.store(directory) as store:
                service = YouTubeResearchService(
                    store,
                    metadata_transport=lambda video_id, url: {
                        "title": "ARCHON overview",
                        "published_at": "2026-11-16T00:00:00Z",
                    },
                    transcript_transport=lambda video_id, url: [
                        {"start_ms": 1000, "end_ms": 2500, "text": "first segment"},
                        {"start_ms": 2500, "end_ms": 4000, "text": "second segment"},
                    ],
                    clock=lambda: OBSERVED,
                )
                result = service.fetch(URL)
                self.assertEqual(result.status, "ok")
                self.assertEqual(result.record.video_id, "abc123")
                self.assertEqual(result.record.transcript[0].start_ms, 1000)
                self.assertEqual(result.record.transcript[0].source_link, URL + "#t=1s")
                saved = store.latest("abc123")
                self.assertEqual(saved.as_dict(), result.record.as_dict())

    def test_transcript_failure_reason_is_persisted(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.store(directory) as store:
                service = YouTubeResearchService(
                    store,
                    metadata_transport=lambda *_args: {"title": "video"},
                    transcript_transport=lambda *_args: (_ for _ in ()).throw(TimeoutError("provider details")),
                    clock=lambda: OBSERVED,
                )
                result = service.fetch(URL)
                self.assertEqual((result.status, result.failure_reason), ("partial", "provider_timeout"))
                saved = store.latest("abc123")
                self.assertEqual(saved.failure_reason, "provider_timeout")
                self.assertNotIn("provider details", str(saved.as_dict()))

    def test_invalid_url_is_blocked_before_provider_calls(self):
        called = []
        with tempfile.TemporaryDirectory() as directory:
            with self.store(directory) as store:
                service = YouTubeResearchService(
                    store,
                    metadata_transport=lambda *_args: called.append(True) or {},
                    clock=lambda: OBSERVED,
                )
                result = service.fetch("https://evil.example/watch?v=abc123")
                self.assertEqual((result.status, result.failure_reason), ("blocked", "invalid_video_url"))
                self.assertEqual(called, [])

    def test_invalid_offsets_are_failed_and_persisted(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.store(directory) as store:
                service = YouTubeResearchService(
                    store,
                    metadata_transport=lambda *_args: {"title": "video"},
                    transcript_transport=lambda *_args: [{"start_ms": 2000, "end_ms": 1000, "text": "bad"}],
                    clock=lambda: OBSERVED,
                )
                result = service.fetch(URL)
                self.assertEqual((result.status, result.failure_reason), ("failed", "provider_invalid"))
                self.assertEqual(store.latest("abc123").failure_reason, "provider_invalid")

    def test_missing_metadata_transport_is_persisted(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.store(directory) as store:
                result = YouTubeResearchService(store, clock=lambda: OBSERVED).fetch(URL)
                self.assertEqual((result.status, result.failure_reason), ("failed", "metadata_unavailable"))
                self.assertEqual(store.latest("abc123").status, "failed")

    def test_supported_url_forms_return_the_same_id(self):
        self.assertEqual(video_id_from_url(URL), "abc123")
        self.assertEqual(video_id_from_url("https://youtu.be/abc123"), "abc123")
        self.assertEqual(video_id_from_url("https://youtube.com/shorts/abc123"), "abc123")


if __name__ == "__main__":
    unittest.main()
