import json
from pathlib import Path


def test_benchmark_fixtures_cover_admitted_strategies() -> None:
    path = Path("tests/fixtures/benchmarks/admitted_strategy_fixtures.json")
    record = json.loads(path.read_text(encoding="utf-8"))

    strategies = {fixture["strategy"] for fixture in record["fixtures"]}

    assert record["schema_version"] == "catalyst.benchmark_fixtures.v1"
    assert {
        "paragraph_group",
        "recursive_fallback",
        "hierarchical",
        "ast_code",
        "semantic_refinement",
    } <= strategies
    assert all(fixture["text"].strip() for fixture in record["fixtures"])
