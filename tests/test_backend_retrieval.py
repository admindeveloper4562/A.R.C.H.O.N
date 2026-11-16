import tempfile
import unittest
from pathlib import Path

from jarvis_v2.backend import DocumentStore, LocalEmbeddingReranker, RetrievalError


class BackendRetrievalTests(unittest.TestCase):
    def test_search_returns_scope_source_timestamp_and_citation(self):
        with tempfile.TemporaryDirectory() as directory:
            with DocumentStore(Path(directory) / "retrieval.sqlite") as store:
                store.add_document(
                    "doc-1", "ARCHON deterministic routing", source_id="docs-1",
                    source_uri="docs/architecture.md", access_scope="public_metadata",
                    citation="architecture.md#routing", title="Routing",
                    observed_at="2026-11-16T00:00:00Z",
                )
                store.add_document(
                    "doc-2", "ARCHON private routing", source_id="docs-2",
                    source_uri="private/notes.md", access_scope="scoped_private",
                    citation="notes.md#routing", title="Private",
                )
                results = store.search("deterministic routing", access_scope="public_metadata")
                self.assertEqual(len(results), 1)
                self.assertTrue(
                    {"access_scope", "source_id", "observed_at", "citation"} <= set(results[0]),
                )
                self.assertEqual(results[0]["citation"], "architecture.md#routing")
                self.assertEqual(store.search("private routing", access_scope="public_metadata"), [])

    def test_source_filter_and_replay_are_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            with DocumentStore(Path(directory) / "retrieval.sqlite") as store:
                values = {
                    "source_id": "docs-1", "source_uri": "docs/a.md",
                    "access_scope": "public_metadata", "citation": "a.md#1",
                    "title": "A",
                }
                first = store.add_document("doc-1", "alpha source", **values)
                self.assertEqual(first, store.add_document("doc-1", "alpha source", **values))
                self.assertEqual(store.search("alpha", access_scope="public_metadata", source_id="missing"), [])
                with self.assertRaises(RetrievalError):
                    store.add_document("doc-1", "changed", **values)

    def test_invalid_queries_and_unbounded_documents_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with DocumentStore(Path(directory) / "retrieval.sqlite") as store:
                values = {
                    "source_id": "docs-1", "source_uri": "docs/a.md",
                    "access_scope": "public_metadata", "citation": "a.md#1",
                }
                with self.assertRaises(RetrievalError):
                    store.search("", access_scope="public_metadata")
                with self.assertRaises(RetrievalError):
                    store.add_document("doc-1", "x" * (512 * 1024 + 1), **values)
                with self.assertRaises(RetrievalError):
                    store.add_document("doc-1", "alpha", access_scope="bad scope", **{k: v for k, v in values.items() if k != "access_scope"})

    def test_optional_reranker_preserves_search_result_shape(self):
        with tempfile.TemporaryDirectory() as directory:
            with DocumentStore(Path(directory) / "retrieval.sqlite") as store:
                store.add_document(
                    "doc-1", "blue house", source_id="docs-1",
                    source_uri="docs/a.md", access_scope="public_metadata",
                    citation="a.md#1",
                )
                store.add_document(
                    "doc-2", "green garden", source_id="docs-1",
                    source_uri="docs/b.md", access_scope="public_metadata",
                    citation="b.md#1",
                )
                results = store.search(
                    "blue house", access_scope="public_metadata",
                    reranker=LocalEmbeddingReranker(),
                )
                self.assertEqual(results[0]["document_id"], "doc-1")
                self.assertIn("citation", results[0])


if __name__ == "__main__":
    unittest.main()
