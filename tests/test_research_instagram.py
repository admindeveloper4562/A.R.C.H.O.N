from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest

from jarvis_v2.research import InstagramReelStore, InstagramReelService, instagram_reel_id_from_url


OBSERVED = datetime(2026, 11, 17, 1, 2, 3, tzinfo=timezone.utc)
URL = "https://www.instagram.com/reel/Reel_123/"


class ResearchInstagramTests(unittest.TestCase):
    def store(self, directory):
        return InstagramReelStore(Path(directory) / "research.sqlite")

    def test_public_metadata_caption_audio_and_source_links_persist(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.store(directory) as store:
                service = InstagramReelService(
                    store,
                    metadata_transport=lambda reel_id, url: {"title": "Reel", "caption": "caption"},
                    audio_transport=lambda reel_id, url: [
                        {"start_ms": 500, "end_ms": 1500, "text": "spoken"},
                    ],
                    clock=lambda: OBSERVED,
                )
                result = service.fetch(URL)
                self.assertEqual(result.status, "ok")
                self.assertEqual(result.record.reel_id, "Reel_123")
                self.assertEqual(result.record.caption, "caption")
                self.assertEqual(result.record.audio_segments[0].source_link, URL + "#t=0.5s")
                self.assertEqual(store.latest("Reel_123").as_dict(), result.record.as_dict())

    def test_private_content_is_blocked_without_audio_access(self):
        called = []
        with tempfile.TemporaryDirectory() as directory:
            with self.store(directory) as store:
                service = InstagramReelService(
                    store,
                    metadata_transport=lambda *_args: {"is_private": True},
                    audio_transport=lambda *_args: called.append(True) or [],
                    clock=lambda: OBSERVED,
                )
                result = service.fetch(URL)
                self.assertEqual((result.status, result.failure_reason), ("blocked", "private_content_unavailable"))
                self.assertEqual(called, [])
                self.assertEqual(store.latest("Reel_123").failure_reason, "private_content_unavailable")

    def test_login_required_content_is_blocked_transparently(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.store(directory) as store:
                service = InstagramReelService(
                    store,
                    metadata_transport=lambda *_args: {"requires_login": True},
                    clock=lambda: OBSERVED,
                )
                result = service.fetch(URL)
                self.assertEqual((result.status, result.failure_reason), ("blocked", "private_content_unavailable"))

    def test_audio_unavailable_is_partial_with_persisted_reason(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.store(directory) as store:
                service = InstagramReelService(
                    store,
                    metadata_transport=lambda *_args: {"caption": "public"},
                    clock=lambda: OBSERVED,
                )
                result = service.fetch(URL)
                self.assertEqual((result.status, result.failure_reason), ("partial", "audio_unavailable"))
                self.assertEqual(store.latest("Reel_123").failure_reason, "audio_unavailable")

    def test_invalid_url_is_blocked_before_provider_calls(self):
        called = []
        with tempfile.TemporaryDirectory() as directory:
            with self.store(directory) as store:
                service = InstagramReelService(
                    store,
                    metadata_transport=lambda *_args: called.append(True) or {},
                    clock=lambda: OBSERVED,
                )
                result = service.fetch("https://instagram.example/reel/Reel_123/")
                self.assertEqual((result.status, result.failure_reason), ("blocked", "invalid_reel_url"))
                self.assertEqual(called, [])

    def test_invalid_audio_offsets_are_failed_and_persisted(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.store(directory) as store:
                service = InstagramReelService(
                    store,
                    metadata_transport=lambda *_args: {"title": "Reel"},
                    audio_transport=lambda *_args: [{"start_ms": 1000, "end_ms": 500, "text": "bad"}],
                    clock=lambda: OBSERVED,
                )
                result = service.fetch(URL)
                self.assertEqual((result.status, result.failure_reason), ("failed", "provider_invalid"))
                self.assertEqual(store.latest("Reel_123").failure_reason, "provider_invalid")

    def test_supported_reel_url_forms(self):
        self.assertEqual(instagram_reel_id_from_url(URL), "Reel_123")
        self.assertEqual(instagram_reel_id_from_url("https://instagram.com/reels/Reel_123/"), "Reel_123")
        self.assertEqual(instagram_reel_id_from_url("https://www.instagram.com/p/Reel_123/"), "Reel_123")


if __name__ == "__main__":
    unittest.main()
