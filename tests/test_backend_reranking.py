import time
import unittest

from jarvis_v2.backend import HardwareBudget, LocalEmbeddingReranker


def candidate(document_id, snippet):
    return {"document_id": document_id, "snippet": snippet}


class BackendRerankingTests(unittest.TestCase):
    def test_local_embedding_reranks_with_stable_ties(self):
        reranker = LocalEmbeddingReranker(budget=HardwareBudget(dimensions=8))
        result = reranker.rerank(
            "blue house",
            [candidate("a", "red house"), candidate("b", "blue house")],
        )
        self.assertTrue(result.used_embeddings)
        self.assertEqual([item["document_id"] for item in result], ["b", "a"])
        self.assertIsNone(result.fallback_reason)

    def test_budget_falls_back_to_keyword_order(self):
        reranker = LocalEmbeddingReranker(
            budget=HardwareBudget(max_candidates=1),
        )
        result = reranker.rerank(
            "blue house",
            [candidate("a", "unrelated"), candidate("b", "blue house")],
        )
        self.assertFalse(result.used_embeddings)
        self.assertEqual(result.fallback_reason, "candidate_limit")
        self.assertEqual([item["document_id"] for item in result], ["b", "a"])

    def test_model_failure_falls_back_without_provider_substitution(self):
        def broken(_text):
            raise RuntimeError("local model unavailable")

        result = LocalEmbeddingReranker(embedder=broken).rerank(
            "blue",
            [candidate("a", "blue"), candidate("b", "green")],
        )
        self.assertFalse(result.used_embeddings)
        self.assertEqual(result.fallback_reason, "embedding_error")
        self.assertEqual(result[0]["document_id"], "a")

    def test_slow_model_is_time_bounded_and_falls_back(self):
        def slow(_text):
            time.sleep(0.2)
            return (1.0, 0.0)

        start = time.monotonic()
        result = LocalEmbeddingReranker(
            budget=HardwareBudget(max_time_ms=20), embedder=slow
        ).rerank("blue", [candidate("a", "blue")])
        elapsed = time.monotonic() - start
        self.assertFalse(result.used_embeddings)
        self.assertEqual(result.fallback_reason, "time_budget")
        self.assertLess(elapsed, 0.15)

    def test_invalid_vectors_fall_back(self):
        result = LocalEmbeddingReranker(embedder=lambda _text: (float("nan"),)).rerank(
            "blue", [candidate("a", "blue")]
        )
        self.assertFalse(result.used_embeddings)
        self.assertEqual(result.fallback_reason, "embedding_error")


if __name__ == "__main__":
    unittest.main()
