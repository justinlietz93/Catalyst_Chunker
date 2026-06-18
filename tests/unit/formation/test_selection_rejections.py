from catalyst.formation.candidates.candidate_metrics import CandidateMetrics
from catalyst.formation.candidates.candidate_reason import CandidateReason
from catalyst.formation.candidates.chunk_candidate import ChunkCandidate
from catalyst.formation.candidates.chunk_candidate_set import ChunkCandidateSet
from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.formation.selection.selector import SelectionFailure, select_candidate_set
from catalyst.source.records.source_span import SourceSpan


def test_selector_preserves_rejection_records() -> None:
    span = SourceSpan(
        source_id="src",
        start_byte=0,
        end_byte=5,
        start_char=0,
        end_char=5,
    )
    oversized = ChunkCandidate(
        candidate_id="cand_bad",
        source_id="src",
        spans=(span,),
        text="too large",
        token_count=99,
        evidence_ids=("obs_bad",),
        reason_ids=("reason_bad",),
        metrics=CandidateMetrics(token_count=99, boundary_count=0),
    )
    accepted = ChunkCandidate(
        candidate_id="cand_ok",
        source_id="src",
        spans=(span,),
        text="ok",
        token_count=1,
        evidence_ids=("obs_ok",),
        reason_ids=("reason_ok",),
        metrics=CandidateMetrics(token_count=1, boundary_count=0),
    )

    result = select_candidate_set(
        (
            ChunkCandidateSet(
                candidate_set_id="bad_set",
                strategy="fixture",
                source_id="src",
                candidates=(oversized,),
                reasons=(),
            ),
            ChunkCandidateSet(
                candidate_set_id="ok_set",
                strategy="fixture",
                source_id="src",
                candidates=(accepted,),
                reasons=(),
            ),
        ),
        SelectionPolicy(hard_max_tokens=10),
    )

    assert result.accepted.candidate_set_id == "ok_set"
    assert len(result.rejections) == 1
    assert result.rejections[0].reason == "candidate set violates hard token budget"


def test_selector_failure_exposes_rejection_records() -> None:
    try:
        select_candidate_set(
            (
                ChunkCandidateSet(
                    candidate_set_id="empty_set",
                    strategy="fixture",
                    source_id="src",
                    candidates=(),
                    reasons=(
                        CandidateReason(
                            reason_id="reason_empty",
                            kind="malformed_fixture",
                            evidence_ids=("obs_bad",),
                            description="fixture malformed evidence",
                        ),
                    ),
                ),
            ),
            SelectionPolicy(),
        )
    except SelectionFailure as error:
        assert len(error.rejections) == 1
        assert error.rejections[0].reason == "candidate set contains no candidates"
        assert error.rejections[0].evidence_ids == ("obs_bad",)
    else:
        raise AssertionError("selection should fail without an accepted candidate set")
