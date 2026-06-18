from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.formation.strategies.paragraph_group_strategy import ParagraphGroupStrategy
from catalyst.formation.strategies.semantic_refinement_strategy import SemanticRefinementStrategy
from catalyst.observation.evidence.evidence_set import EvidenceSet
from catalyst.observation.instruments.collect import observe_source
from catalyst.observation.instruments.semantic_shift_instrument import SemanticShiftInstrument
from catalyst.source.records.source_record import SourceRecord


def test_semantic_refinement_requires_policy_permission() -> None:
    source, evidence = _source_with_semantic_shift()
    structural = ParagraphGroupStrategy().form(source, evidence, SelectionPolicy(target_tokens=100))

    candidate_set = SemanticRefinementStrategy().form(
        source,
        evidence,
        SelectionPolicy(allow_semantic_refinement=False),
        structural_candidate_set=structural,
    )

    assert candidate_set.candidates == ()
    assert candidate_set.reasons[0].kind == "semantic_refinement_policy_disabled"


def test_semantic_refinement_requires_shift_evidence() -> None:
    source = SourceRecord.from_bytes(
        b"Alpha beta gamma define the first topic.\n\n"
        b"Zinc copper nickel describe another domain.\n",
        source_kind="text",
    )
    evidence = observe_source(source)
    policy = SelectionPolicy(target_tokens=100, allow_semantic_refinement=True)
    structural = ParagraphGroupStrategy().form(source, evidence, policy)

    candidate_set = SemanticRefinementStrategy().form(
        source,
        evidence,
        policy,
        structural_candidate_set=structural,
    )

    assert candidate_set.candidates == ()
    assert candidate_set.reasons[0].kind == "semantic_refinement_requires_shift_evidence"


def test_semantic_refinement_splits_existing_structural_candidate() -> None:
    source, evidence = _source_with_semantic_shift()
    policy = SelectionPolicy(target_tokens=100, hard_max_tokens=100, allow_semantic_refinement=True)
    structural = ParagraphGroupStrategy().form(source, evidence, policy)

    candidate_set = SemanticRefinementStrategy().form(
        source,
        evidence,
        policy,
        structural_candidate_set=structural,
    )

    assert structural.strategy == "paragraph_group"
    assert len(structural.candidates) == 1
    assert candidate_set.strategy == "semantic_refinement"
    assert len(candidate_set.candidates) == 2
    assert all("semantic_shift" not in reason.kind for reason in structural.reasons)
    assert all(candidate.warnings == ("formed by semantic refinement evidence",) for candidate in candidate_set.candidates)
    assert all(
        evidence.by_id(evidence_id).kind != "semantic_shift"
        for evidence_id in structural.candidates[0].evidence_ids
    )
    assert any(
        evidence.by_id(evidence_id).kind == "semantic_shift"
        for candidate in candidate_set.candidates
        for evidence_id in candidate.evidence_ids
    )


def _source_with_semantic_shift() -> tuple[SourceRecord, EvidenceSet]:
    source = SourceRecord.from_bytes(
        b"Alpha beta gamma define the first topic.\n\n"
        b"Zinc copper nickel describe another domain.\n",
        source_kind="text",
    )
    base = observe_source(source)
    semantic = SemanticShiftInstrument(minimum_discontinuity=0.5).observe(source)
    return source, EvidenceSet(base.source_id, (*base.observations, *semantic))
