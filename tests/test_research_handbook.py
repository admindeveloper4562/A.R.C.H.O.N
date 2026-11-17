from datetime import datetime, timezone
import unittest

from jarvis_v2.research import (
    HandbookEditProposalV1,
    HandbookGovernanceError,
    HandbookOwnerApproval,
    HandbookProposalWorkflow,
    HandbookReviewReceipt,
    sha256_text,
)


WHEN = datetime(2026, 11, 17, 2, 10, 0, tzinfo=timezone.utc).isoformat()
BASE = sha256_text("handbook base")


class ResearchHandbookTests(unittest.TestCase):
    def proposal(self, *, proposal_id="proposal-1", section="tips", role="research", candidate="# tip\n"):
        return HandbookEditProposalV1(
            proposal_id=proposal_id,
            handbook_path="CODING_HANDBOOK.md",
            base_digest=BASE,
            candidate_digest=sha256_text(candidate),
            section=section,
            actor_role=role,
            actor_id="research-1",
            operation="append",
            entry_id="entry-1",
            supersedes=None,
            content_digest=sha256_text("tip evidence"),
            reason="bounded source-linked development tip",
            regression_evidence="tests/test_research_handbook.py::test_tip_round_trip",
            created_at_utc=WHEN,
        )

    def review(self, proposal, *, reviewer="qc-1", decision="approved"):
        return HandbookReviewReceipt(
            receipt_id="review-1",
            proposal_id=proposal.proposal_id,
            candidate_digest=proposal.candidate_digest,
            reviewer_id=reviewer,
            reviewer_role="qc",
            decision=decision,
            evidence_ref="qc-artifact-1",
            reviewed_at_utc=WHEN,
        )

    def test_research_tip_round_trip_requires_review_and_merger(self):
        candidate = "# tip\n"
        proposal = self.proposal(candidate=candidate)
        workflow = HandbookProposalWorkflow()

        self.assertEqual(workflow.submit(proposal, candidate_content=candidate).state, "PROPOSED")
        with self.assertRaisesRegex(HandbookGovernanceError, "approval"):
            workflow.queue_for_merge(proposal.proposal_id, current_base_digest=BASE)

        self.assertEqual(workflow.review(proposal.proposal_id, self.review(proposal)).state, "APPROVED")
        self.assertEqual(
            workflow.queue_for_merge(proposal.proposal_id, current_base_digest=BASE).state,
            "MERGE_QUEUED",
        )
        result = workflow.merge(
            proposal.proposal_id,
            merger_id="serialized-merger",
            current_base_digest=BASE,
            applied_candidate_digest=proposal.candidate_digest,
        )
        self.assertEqual(result.state, "VERIFIED")
        self.assertEqual(result.proposal.candidate_digest, sha256_text(candidate))

    def test_research_is_the_only_proposer_for_tips(self):
        workflow = HandbookProposalWorkflow()
        proposal = self.proposal(role="qc")
        with self.assertRaisesRegex(HandbookGovernanceError, "authorized"):
            workflow.submit(proposal)

    def test_review_cannot_self_approve_or_use_stale_candidate(self):
        workflow = HandbookProposalWorkflow()
        proposal = self.proposal()
        workflow.submit(proposal)
        with self.assertRaisesRegex(HandbookGovernanceError, "self"):
            workflow.review(proposal.proposal_id, self.review(proposal, reviewer="research-1"))
        stale = HandbookReviewReceipt(
            "review-2", proposal.proposal_id, sha256_text("other"), "qc-1", "qc",
            "approved", "qc-artifact-2", WHEN,
        )
        with self.assertRaisesRegex(HandbookGovernanceError, "bound"):
            workflow.review(proposal.proposal_id, stale)

    def test_constitution_requires_distinct_owner_receipt(self):
        workflow = HandbookProposalWorkflow()
        proposal = self.proposal(section="constitution", role="research")
        workflow.submit(proposal)
        workflow.review(proposal.proposal_id, self.review(proposal))
        with self.assertRaisesRegex(HandbookGovernanceError, "owner"):
            workflow.queue_for_merge(proposal.proposal_id, current_base_digest=BASE)
        approval = HandbookOwnerApproval(
            "owner-1", proposal.proposal_id, proposal.candidate_digest, "owner-1", WHEN,
        )
        workflow.owner_approve(proposal.proposal_id, approval)
        self.assertEqual(
            workflow.queue_for_merge(proposal.proposal_id, current_base_digest=BASE).state,
            "MERGE_QUEUED",
        )

    def test_stale_base_blocks_without_mutating_the_candidate(self):
        workflow = HandbookProposalWorkflow()
        proposal = self.proposal()
        workflow.submit(proposal)
        workflow.review(proposal.proposal_id, self.review(proposal))
        with self.assertRaisesRegex(HandbookGovernanceError, "stale"):
            workflow.queue_for_merge(proposal.proposal_id, current_base_digest=sha256_text("new base"))
        record = workflow.get(proposal.proposal_id)
        self.assertEqual(record.state, "BLOCKED")
        self.assertEqual(record.proposal.candidate_digest, proposal.candidate_digest)

    def test_replay_is_idempotent_and_conflicting_payload_is_rejected(self):
        workflow = HandbookProposalWorkflow()
        proposal = self.proposal()
        first = workflow.submit(proposal)
        second = workflow.submit(proposal)
        self.assertEqual(first.as_dict(), second.as_dict())
        conflicting = self.proposal(candidate="# different\n")
        with self.assertRaisesRegex(HandbookGovernanceError, "conflicting"):
            workflow.submit(conflicting)

    def test_proposal_envelope_rejects_aliases_and_unknown_fields(self):
        proposal = self.proposal()
        values = proposal.as_dict()
        values["extra"] = "not part of v1"
        with self.assertRaisesRegex(HandbookGovernanceError, "fields"):
            HandbookEditProposalV1.from_dict(values)
        with self.assertRaisesRegex(HandbookGovernanceError, "canonical"):
            HandbookEditProposalV1(**{**proposal.as_dict(), "handbook_path": "./CODING_HANDBOOK.md"})


if __name__ == "__main__":
    unittest.main()
