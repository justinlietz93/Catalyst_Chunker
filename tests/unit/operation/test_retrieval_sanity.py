import json
from pathlib import Path

from catalyst.boundary.adapters.ast_python.python_ast_parser import PythonAstParser
from catalyst.operation.commands.evaluate_retrieval_sanity import evaluate_retrieval_sanity


FIXTURE_PATH = Path("tests/fixtures/retrieval_sanity/heldout_fixtures.json")


def test_retrieval_sanity_fixtures_cover_source_families_and_strategies() -> None:
    record = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    fixtures = record["fixtures"]

    families = {fixture["source_family"] for fixture in fixtures}
    strategies = {strategy for fixture in fixtures for strategy in fixture["strategies"]}

    assert record["schema_version"] == "catalyst.retrieval_sanity_fixtures.v1"
    assert {"markdown", "plain_text", "code", "weak_structure"} <= families
    assert all(fixture["query"] for fixture in fixtures)
    assert all(fixture["relevant_source_spans"] for fixture in fixtures)
    assert all(fixture["expected_relevant_terms"] for fixture in fixtures)
    assert {
        "paragraph_group",
        "recursive_fallback",
        "dynamic_token_sizing",
        "hierarchical",
        "ast_code",
        "semantic_refinement",
    } <= strategies


def test_retrieval_sanity_report_compares_quality_cost_and_hard_invariants() -> None:
    fixtures = tuple(json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["fixtures"])

    record = evaluate_retrieval_sanity(fixtures, ast_parser=PythonAstParser()).record()

    assert record["schema_version"] == "catalyst.retrieval_sanity.v1"
    assert record["projection_kind"] == "retrieval_sanity"
    assert record["authority"] == {
        "diagnostic_only": True,
        "hard_invariants_override_scores": True,
    }
    strategy_results = [
        result
        for fixture in record["fixtures"]
        for result in fixture["strategy_results"]
    ]
    assert {result["strategy"] for result in strategy_results} >= {
        "paragraph_group",
        "recursive_fallback",
        "dynamic_token_sizing",
        "hierarchical",
        "ast_code",
        "semantic_refinement",
    }
    assert all("retrieval_quality" in result for result in strategy_results)
    assert all("retrieval_metrics" in result for result in strategy_results)
    assert all("cost" in result for result in strategy_results)
    assert all("hard_invariants" in result for result in strategy_results)
    assert all(
        result["retrieval_metrics"]["ranking_method"] == "lexical_query_overlap.v1"
        for result in strategy_results
    )
    assert all("recall_at_1" in result["retrieval_metrics"] for result in strategy_results)
    assert all("recall_at_3" in result["retrieval_metrics"] for result in strategy_results)
    assert all("mrr" in result["retrieval_metrics"] for result in strategy_results)
    assert any(result["hard_invariants_passed"] is False for result in strategy_results)
    assert any(
        result["retrieval_quality"]["answer_context_adequacy"] == 1.0
        for result in strategy_results
    )
    assert any(result["retrieval_metrics"]["mrr"] == 1.0 for result in strategy_results)
    assert any(result["retrieval_metrics"]["recall_at_1"] == 1.0 for result in strategy_results)
    assert all(
        result["hard_invariants_passed"] is False
        or result["retrieval_metrics"]["relevant_candidate_count"] >= 1
        for result in strategy_results
    )


def test_ast_code_sanity_requires_ast_parser_port() -> None:
    fixture = {
        "fixture_id": "python_call_dependency",
        "source_family": "code",
        "source_kind": "code",
        "query": "Which caller invokes helper?",
        "expected_terms": ["caller", "helper"],
        "expected_relevant_terms": ["caller", "helper"],
        "relevant_source_spans": [{"start_char": 28, "end_char": 61}],
        "strategies": ["ast_code"],
        "text": "def helper():\n    return 1\n\ndef caller():\n    return helper()\n",
    }

    without_parser = evaluate_retrieval_sanity((fixture,)).record()
    with_parser = evaluate_retrieval_sanity((fixture,), ast_parser=PythonAstParser()).record()

    unavailable = without_parser["fixtures"][0]["strategy_results"][0]
    available = with_parser["fixtures"][0]["strategy_results"][0]
    assert unavailable["available"] is False
    assert unavailable["hard_invariants_passed"] is False
    assert available["available"] is True
    assert available["hard_invariants_passed"] is True
    assert available["retrieval_quality"]["answer_context_adequacy"] == 1.0
    assert available["retrieval_metrics"]["mrr"] == 1.0
    assert available["retrieval_metrics"]["recall_at_1"] == 1.0
