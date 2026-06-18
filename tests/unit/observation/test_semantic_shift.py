from catalyst.observation.evidence.semantic_shift_observation import SemanticShiftObservation
from catalyst.observation.instruments.collect import observe_source
from catalyst.observation.instruments.paragraph_instrument import ParagraphInstrument
from catalyst.observation.instruments.semantic_shift_instrument import SemanticShiftInstrument
from catalyst.source.records.source_record import SourceRecord


def test_semantic_shift_instrument_emits_evidence_only_observation() -> None:
    source = SourceRecord.from_bytes(
        b"Alpha beta gamma define the first topic.\n\n"
        b"Zinc copper nickel describe another domain.\n",
        source_kind="text",
    )

    observations = SemanticShiftInstrument(minimum_discontinuity=0.5).observe(source)

    assert len(observations) == 1
    observation = observations[0]
    assert observation.kind == "semantic_shift"
    assert observation.payload["evidence_family"] == "semantic"
    assert observation.payload["model_identity"] == "local-lexical-v1"
    assert observation.payload["policy_id"] == "semantic-refinement-optional"
    assert observation.payload["source_truth"] is False


def test_baseline_observation_does_not_run_semantic_shift() -> None:
    source = SourceRecord.from_bytes(
        b"Alpha beta gamma define the first topic.\n\n"
        b"Zinc copper nickel describe another domain.\n",
        source_kind="text",
    )

    evidence = observe_source(source)

    assert not evidence.by_kind("semantic_shift")


def test_semantic_shift_observation_validates_source_lineage() -> None:
    source = SourceRecord.from_bytes(b"One topic.\n\nAnother topic.\n", source_kind="text")
    left, right = ParagraphInstrument().observe(source)

    observation = SemanticShiftObservation(
        left_span=left.span,
        right_span=right.span,
        discontinuity=0.8,
        model_identity="fixture-model",
        policy_id="fixture-policy",
    ).to_observation(source)

    assert observation.span.source_id == source.source_id
    assert observation.payload["left_span"]["source_id"] == source.source_id
    assert observation.payload["right_span"]["source_id"] == source.source_id
