from catalyst.formation.candidates.chunk_candidate_set import ChunkCandidateSet
from catalyst.invariant.checks.fallback_evidence_check import check_fallback_evidence


def test_fallback_candidate_set_requires_evidence() -> None:
    bad = ChunkCandidateSet(
        candidate_set_id="fixed",
        strategy="fixed_size_fallback",
        source_id="src",
        candidates=(),
        reasons=(),
    )

    result = check_fallback_evidence((bad,))

    assert not result.passed
    assert result.invariant_id == "I006"
