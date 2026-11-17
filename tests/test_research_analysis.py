from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest

from jarvis_v2.research import MediaAnalysisService, MediaAnalysisStore


OBSERVED = datetime(2026, 11, 17, 1, 2, 3, tzinfo=timezone.utc)


class ResearchAnalysisTests(unittest.TestCase):
    def store(self, directory):
        return MediaAnalysisStore(Path(directory) / "analysis.sqlite")

    def test_permission_and_modality_are_recorded_with_timestamped_finding(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.store(directory) as store:
                calls = []

                def analyze(media_id, media_kind, start_ms, end_ms):
                    calls.append((media_id, media_kind, start_ms, end_ms))
                    return {"finding": "visual context"}

                service = MediaAnalysisService(store, analyzer=analyze, clock=lambda: OBSERVED)
                result = service.analyze("abc123", "youtube", 1000, 2000, modality="audio_visual", permission_granted=True)
                self.assertEqual(result.status, "ok")
                self.assertEqual(result.evidence.observed_at, "2026-11-17T01:02:03.000000Z")
                self.assertEqual(result.evidence.finding, "visual context")
                self.assertEqual(calls, [("abc123", "youtube", 1000, 2000)])
                self.assertEqual(store.latest("abc123").as_dict(), result.evidence.as_dict())

    def test_permission_denial_is_persisted_without_analyzer_call(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.store(directory) as store:
                called = []
                service = MediaAnalysisService(
                    store,
                    analyzer=lambda *_args: called.append(True) or {"finding": "not used"},
                    clock=lambda: OBSERVED,
                )
                result = service.analyze("abc123", "instagram", 0, 1000, modality="audio", permission_granted=False)
                self.assertEqual((result.status, result.evidence.failure_reason), ("blocked", "permission_required"))
                self.assertEqual(called, [])
                self.assertEqual(store.latest("abc123").status, "blocked")

    def test_missing_analyzer_and_empty_finding_are_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.store(directory) as store:
                result = MediaAnalysisService(store, clock=lambda: OBSERVED).analyze(
                    "abc123", "youtube", 0, 1000, modality="video", permission_granted=True
                )
                self.assertEqual((result.status, result.evidence.failure_reason), ("failed", "analyzer_unavailable"))

                empty = MediaAnalysisService(
                    store, analyzer=lambda *_args: {"finding": ""}, clock=lambda: OBSERVED
                ).analyze("abc123", "youtube", 1000, 2000, modality="video", permission_granted=True)
                self.assertEqual((empty.status, empty.evidence.failure_reason), ("empty", "analyzer_empty"))

    def test_provider_failure_is_redacted_and_persisted(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.store(directory) as store:
                def timeout(*_args):
                    raise TimeoutError("provider internals")

                result = MediaAnalysisService(store, analyzer=timeout, clock=lambda: OBSERVED).analyze(
                    "abc123", "youtube", 0, 1000, modality="audio", permission_granted=True
                )
                self.assertEqual(result.evidence.failure_reason, "provider_timeout")
                self.assertNotIn("provider internals", str(result.as_dict()))

    def test_invalid_offsets_or_modality_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.store(directory) as store:
                service = MediaAnalysisService(store)
                with self.assertRaisesRegex(ValueError, "offsets"):
                    service.analyze("abc123", "youtube", 1000, 1000, modality="audio", permission_granted=True)
                with self.assertRaisesRegex(ValueError, "modality"):
                    service.analyze("abc123", "youtube", 0, 1000, modality="text", permission_granted=True)


if __name__ == "__main__":
    unittest.main()
