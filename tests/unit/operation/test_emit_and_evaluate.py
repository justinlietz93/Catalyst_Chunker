from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.operation.commands.chunk_source import chunk_source
from catalyst.operation.commands.emit_projection import emit_boundary_inspection, emit_projection
from catalyst.operation.commands.evaluate_candidates import evaluate_candidates


def test_emit_projection_returns_versioned_records() -> None:
    result = chunk_source(b"# Title\n\nBody text.")

    retrieval = emit_projection(result, "retrieval")
    audit = emit_projection(result, "audit")

    assert isinstance(retrieval, list)
    assert retrieval[0]["schema_version"] == "catalyst.retrieval.v1"
    assert isinstance(audit, dict)
    assert audit["schema_version"] == "catalyst.audit.v1"


def test_audit_projection_distinguishes_semantic_evidence() -> None:
    result = chunk_source(
        b"Alpha beta gamma define the first topic.\n\n"
        b"Zinc copper nickel describe another domain.\n",
        policy=SelectionPolicy(
            target_tokens=100,
            hard_max_tokens=100,
            allow_semantic_refinement=True,
        ),
    )

    audit = emit_projection(result, "audit")

    assert isinstance(audit, dict)
    assert audit["evidence"]["semantic"]
    assert audit["evidence"]["structural"]
    assert audit["evidence"]["semantic"][0]["model_identity"] == "local-lexical-v1"
    assert audit["evidence"]["semantic"][0]["policy_id"] == "semantic-refinement-optional"


def test_emit_boundary_inspection_returns_versioned_record() -> None:
    record = emit_boundary_inspection(source_id="src", boundary_candidates=())

    assert record["schema_version"] == "catalyst.boundaries.v1"
    assert record["projection_kind"] == "boundary_inspection"


def test_evaluate_candidates_returns_versioned_comparison() -> None:
    record = evaluate_candidates(b"# Title\n\nBody text.").record()

    assert record["schema_version"] == "catalyst.candidate_evaluation.v1"
    assert record["projection_kind"] == "candidate_evaluation"
    assert record["candidate_sets"]
    assert record["accepted_candidate_set"]
    assert record["hard_gate_results"]
    assert record["soft_metrics"]
    assert "selected_graph" in record
    assert record["selected_graph"]["chunks"]


def test_evaluate_candidates_reports_semantic_metrics_when_policy_allows() -> None:
    record = evaluate_candidates(
        b"Alpha beta gamma define the first topic.\n\n"
        b"Zinc copper nickel describe another domain.\n",
        policy=SelectionPolicy(
            target_tokens=100,
            hard_max_tokens=100,
            allow_semantic_refinement=True,
        ),
    ).record()

    assert record["candidate_sets"][0]["strategy"] == "semantic_refinement"
    semantic_id = record["candidate_sets"][0]["candidate_set_id"]
    assert record["soft_metrics"][semantic_id]["semantic_discontinuity"] > 0
    assert record["soft_metrics"][semantic_id]["index_cost_estimate"]["chunk_count"] == 2
    assert record["hard_gate_results"][semantic_id]["passed"] is True
