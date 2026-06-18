from catalyst.observation.evidence.evidence_set import EvidenceSet
from catalyst.observation.evidence.llm_candidate_observation import LlmCandidateObservation
from catalyst.observation.instruments.collect import observe_source
from catalyst.operation.commands.chunk_source import chunk_observed_source
from catalyst.operation.commands.emit_projection import emit_projection
from catalyst.source.records.source_record import SourceRecord


def test_llm_candidate_observation_is_boundary_assisted_evidence_not_source_truth() -> None:
    source = SourceRecord.from_bytes(b"Boundary-assisted candidate source.", source_kind="markdown")

    observation = LlmCandidateObservation(
        span=source.full_span(),
        proposal_text="candidate source",
        prompt_id="prompt_fixture",
        policy_id="policy_fixture",
        model_identity="fixture-llm",
        confidence=0.72,
        rejected_alternatives=("too broad",),
    ).to_observation(source)

    assert observation.kind == "llm_candidate"
    assert observation.payload["evidence_family"] == "boundary_assisted"
    assert observation.payload["source_truth"] is False
    assert observation.payload["rejected_alternatives"] == ["too broad"]


def test_audit_records_llm_prompt_policy_model_confidence_and_rejected_alternatives() -> None:
    source = SourceRecord.from_bytes(b"Boundary-assisted candidate source.", source_kind="markdown")
    base = observe_source(source)
    llm_observation = LlmCandidateObservation(
        span=source.full_span(),
        proposal_text="candidate source",
        prompt_id="prompt_fixture",
        policy_id="policy_fixture",
        model_identity="fixture-llm",
        confidence=0.72,
        rejected_alternatives=("too broad",),
    ).to_observation(source)
    evidence = EvidenceSet(base.source_id, (*base.observations, llm_observation))

    result = chunk_observed_source(source, evidence)
    audit = emit_projection(result, "audit")
    boundary_evidence = audit["evidence"]["boundary_assisted"][0]

    assert boundary_evidence["prompt_id"] == "prompt_fixture"
    assert boundary_evidence["policy_id"] == "policy_fixture"
    assert boundary_evidence["model_identity"] == "fixture-llm"
    assert boundary_evidence["confidence"] == 0.72
    assert boundary_evidence["rejected_alternatives"] == ["too broad"]
