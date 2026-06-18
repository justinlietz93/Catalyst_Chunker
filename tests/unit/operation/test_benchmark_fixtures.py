import json
from pathlib import Path

from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.operation.commands import chunk_source


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


def test_golden_retrieval_corpus_chunk_counts_and_terms() -> None:
    path = Path("tests/fixtures/benchmarks/golden_retrieval_corpus.json")
    record = json.loads(path.read_text(encoding="utf-8"))

    assert record["schema_version"] == "catalyst.golden_retrieval_corpus.v1"
    for fixture in record["fixtures"]:
        policy = SelectionPolicy(**fixture["policy"])
        result = chunk_source(
            fixture["text"].encode("utf-8"),
            source_kind=fixture["source_kind"],
            policy=policy,
        )
        chunk_text = "\n".join(chunk.text.lower() for chunk in result.graph.chunks)
        assert fixture["expected_min_chunks"] <= len(result.graph.chunks)
        assert len(result.graph.chunks) <= fixture["expected_max_chunks"]
        assert all(term in chunk_text for term in fixture["expected_terms"])
