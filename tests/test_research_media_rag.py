from pathlib import Path
import tempfile
import unittest

from jarvis_v2.research import (
    MediaRAGService,
    MediaRAGStore,
    TranscriptSegment,
    VideoRecord,
    chunk_video,
    extract_topics,
)


OBSERVED = "2026-11-17T01:02:03.000000Z"


def record(video_id, text, observed=OBSERVED):
    return VideoRecord(
        video_id,
        f"https://www.youtube.com/watch?v={video_id}",
        f"Video {video_id}",
        None,
        observed,
        "ok",
        (TranscriptSegment(0, 1000, text, f"https://example.test/{video_id}#t=0s"),),
    )


class ResearchMediaRAGTests(unittest.TestCase):
    def test_chunking_is_bounded_reproducible_and_source_linked(self):
        value = record("abc123", "ARCHON research " * 160)
        first = chunk_video(value, max_bytes=256)
        second = chunk_video(value, max_bytes=256)
        self.assertEqual([item.as_dict() for item in first], [item.as_dict() for item in second])
        self.assertGreater(len(first), 1)
        self.assertTrue(all(len(item.text.encode()) <= 256 for item in first))
        self.assertTrue(all(item.source_spans[0].source_link.endswith("#t=0s") for item in first))

    def test_topics_are_stable_and_retain_provenance(self):
        topics = extract_topics(chunk_video(record("abc123", "ARCHON research research provenance")))
        self.assertEqual([(item.term, item.count) for item in topics[:2]], [("research", 2), ("archon", 1)])
        self.assertEqual(topics[0].source_spans[0].video_id, "abc123")

    def test_cross_video_summary_is_sorted_extractive_and_persistent(self):
        with tempfile.TemporaryDirectory() as directory:
            with MediaRAGStore(Path(directory) / "rag.sqlite") as store:
                result = MediaRAGService(store).summarize((
                    record("def456", "Backend retrieval supports citations."),
                    record("abc123", "ARCHON research preserves source spans."),
                ))
                self.assertEqual(result.status, "ok")
                self.assertEqual(result.summary.video_ids, ("abc123", "def456"))
                self.assertIn("abc123", result.summary.text)
                self.assertIn("def456", result.summary.text)
                self.assertTrue(result.summary.source_spans)
                self.assertEqual(store.summary(result.summary.summary_id).as_dict(), result.summary.as_dict())
                self.assertEqual(len(store.chunks_for("abc123")), 1)

    def test_empty_summary_is_explicit(self):
        result = MediaRAGService().summarize(())
        self.assertEqual((result.status, result.summary), ("empty", None))

    def test_invalid_chunk_size_and_duplicate_videos_are_rejected(self):
        value = record("abc123", "bounded text")
        with self.assertRaisesRegex(ValueError, "chunk size"):
            chunk_video(value, max_bytes=32)
        with self.assertRaisesRegex(ValueError, "video set"):
            MediaRAGService().summarize((value, value))


if __name__ == "__main__":
    unittest.main()
