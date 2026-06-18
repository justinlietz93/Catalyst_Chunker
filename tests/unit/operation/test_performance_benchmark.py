import json
from pathlib import Path

from catalyst.operation.commands.evaluate_performance_benchmark import (
    evaluate_performance_benchmark,
)


FIXTURE_PATH = Path("tests/fixtures/benchmarks/performance_benchmark_fixtures.json")


def test_performance_benchmark_fixtures_cover_required_shapes() -> None:
    record = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    fixtures = record["fixtures"]
    families = {fixture["source_family"] for fixture in fixtures}

    assert record["schema_version"] == "catalyst.performance_benchmark_fixtures.v1"
    assert {"large_prose", "code", "markdown", "long_atomic_text"} <= families
    assert all(fixture["strategies"] for fixture in fixtures)


def test_performance_benchmark_reports_diagnostic_resource_shape() -> None:
    fixtures = tuple(json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["fixtures"])

    record = evaluate_performance_benchmark(fixtures).record()

    assert record["schema_version"] == "catalyst.performance_benchmark.v1"
    assert record["projection_kind"] == "performance_benchmark"
    assert record["authority"] == {
        "diagnostic_only": True,
        "not_an_admission_gate": True,
        "machine_dependent_timing": True,
    }
    assert {fixture["source_family"] for fixture in record["fixtures"]} >= {
        "large_prose",
        "code",
        "markdown",
        "long_atomic_text",
    }
    for fixture in record["fixtures"]:
        measures = fixture["source_measures"]
        assert measures["character_count"] > 0
        assert measures["byte_count"] >= measures["character_count"]
        assert measures["lexical_token_count"] >= 1
        for result in fixture["strategy_results"]:
            assert result["status"] == "passed"
            assert result["strategy"]
            assert result["admitted_strategy"]
            assert result["elapsed_time"]["nanoseconds"] >= 0
            assert result["memory"]["measurement"] == "tracemalloc"
            assert result["memory"]["peak_bytes"] >= 0
            assert result["chunk_count"] >= 1
            assert result["token_total"] >= 1
            assert result["repair_count"] >= 0
            assert result["invariant_summary"]["passed"] is True
            assert "I007" in result["invariant_summary"]["invariant_ids"]
