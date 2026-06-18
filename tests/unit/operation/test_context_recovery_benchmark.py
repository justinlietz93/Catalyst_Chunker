import json
from pathlib import Path

from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.operation.commands.evaluate_context_recovery import evaluate_context_recovery


FIXTURE_PATH = Path("tests/fixtures/benchmarks/relation_context_recovery.json")


def test_context_recovery_benchmark_tracks_quality_and_index_cost() -> None:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["fixtures"][0]
    policy = SelectionPolicy(**fixture["policy"])

    record = evaluate_context_recovery(
        fixture["text"].encode("utf-8"),
        expected_terms=tuple(fixture["expected_terms"]),
        policy=policy,
    ).record()

    assert record["schema_version"] == "catalyst.context_recovery_benchmark.v1"
    assert record["projection_kind"] == "context_recovery_benchmark"
    assert record["authority"] == {
        "diagnostic_only": True,
        "does_not_admit_chunks": True,
        "indexed_text_unchanged": True,
    }
    assert record["index_cost"]["chunk_count"] == 2
    assert record["index_cost"]["indexed_token_total"] == 7
    assert record["index_cost"]["relation_count"] == 2
    assert record["context_recovery"]["relation_window_token_total"] == 7
    assert record["retrieval_quality"]["indexed_only"]["answer_context_adequacy"] == 0.5
    assert record["retrieval_quality"]["relation_window"]["answer_context_adequacy"] == 1.0


def test_context_recovery_benchmark_fixture_schema_is_explicit() -> None:
    record = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert record["schema_version"] == "catalyst.context_recovery_benchmark_fixtures.v1"
    assert record["fixtures"][0]["fixture_id"] == "definition_dependency_relation_window"
    assert record["fixtures"][0]["expected_terms"]
