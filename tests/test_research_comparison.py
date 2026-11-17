import unittest

from jarvis_v2.research import (
    ComparisonError,
    SourceClaim,
    SourceComparator,
)


class ResearchComparisonTests(unittest.TestCase):
    def claim(self, source_id, assertion, confidence=None):
        return SourceClaim(
            "release date",
            assertion,
            source_id,
            f"{source_id}#release-date",
            "2026-11-17T02:00:00Z",
            "2026-11-16T00:00:00Z",
            confidence,
        )

    def test_matching_sources_preserve_provenance_and_supplied_confidence(self):
        result = SourceComparator().compare((
            self.claim("docs-a", "2026-11-16", 0.9),
            self.claim("docs-b", "2026-11-16", 0.8),
        ))
        finding = result.findings[0]
        self.assertEqual(result.status, "consistent")
        self.assertEqual(finding.claim_kind, "fact")
        self.assertEqual(finding.confidence, 0.8)
        self.assertEqual(finding.source_ids, ("docs-a", "docs-b"))
        self.assertEqual(len(finding.evidence_refs), 2)

    def test_contradictory_sources_are_uncertain_without_invented_confidence(self):
        result = SourceComparator().compare((
            self.claim("docs-a", "2026-11-16", 0.9),
            self.claim("docs-b", "2026-11-17", 0.9),
        ))
        finding = result.findings[0]
        self.assertEqual(result.status, "contradictory")
        self.assertEqual(finding.claim_kind, "uncertain")
        self.assertIsNone(finding.assertion)
        self.assertIsNone(finding.confidence)
        self.assertEqual(set(finding.contradictory_assertions), {"2026-11-16", "2026-11-17"})

    def test_missing_confidence_stays_unknown_even_when_sources_match(self):
        result = SourceComparator().compare((self.claim("docs-a", "same"),))
        self.assertIsNone(result.findings[0].confidence)

    def test_empty_and_malformed_inputs_are_bounded(self):
        self.assertEqual(SourceComparator().compare(()).status, "empty")
        with self.assertRaisesRegex(ComparisonError, "collection"):
            SourceComparator().compare("not-a-collection")
        with self.assertRaisesRegex(ComparisonError, "confidence"):
            self.claim("docs-a", "claim", 2.0)


if __name__ == "__main__":
    unittest.main()
