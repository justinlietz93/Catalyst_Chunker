"""Evaluate retrieval sanity fixtures without overriding invariants."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import re
from typing import Any

from catalyst.boundary.ports.ast_parser_port import AstParserPort
from catalyst.formation.candidates.chunk_candidate_set import ChunkCandidateSet
from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.formation.strategies.ast_code_strategy import AstCodeStrategy
from catalyst.formation.strategies.hierarchical_strategy import HierarchicalStrategy
from catalyst.formation.strategies.paragraph_group_strategy import ParagraphGroupStrategy
from catalyst.formation.strategies.recursive_fallback_strategy import RecursiveFallbackStrategy
from catalyst.formation.strategies.semantic_refinement_strategy import SemanticRefinementStrategy
from catalyst.invariant.checks.offset_reversibility_check import check_offset_reversibility
from catalyst.invariant.checks.source_coverage_check import check_source_coverage
from catalyst.invariant.checks.source_lineage_check import check_source_lineage
from catalyst.invariant.checks.token_budget_check import check_token_budget
from catalyst.observation.evidence.evidence_set import EvidenceSet
from catalyst.observation.instruments.collect import observe_source
from catalyst.observation.instruments.semantic_shift_instrument import SemanticShiftInstrument
from catalyst.projection.schemas.schema_version import RETRIEVAL_SANITY_SCHEMA_VERSION
from catalyst.source.records.source_record import SourceRecord
from catalyst.source.records.source_span import SourceSpan

_LEXICAL_TOKEN_RE = re.compile(r"\w+")
_RECALL_KS = (1, 3)


@dataclass(frozen=True)
class RetrievalSanityEvaluation:
    """Diagnostic retrieval sanity report."""

    fixture_results: tuple[dict[str, object], ...]

    def record(self) -> dict[str, object]:
        return {
            "schema_version": RETRIEVAL_SANITY_SCHEMA_VERSION,
            "projection_kind": "retrieval_sanity",
            "authority": {
                "diagnostic_only": True,
                "hard_invariants_override_scores": True,
            },
            "fixtures": list(self.fixture_results),
        }


def evaluate_retrieval_sanity(
    fixtures: tuple[Mapping[str, object], ...],
    *,
    ast_parser: AstParserPort | None = None,
) -> RetrievalSanityEvaluation:
    """Compare retrieval sanity fixtures across candidate strategies."""

    results = tuple(_evaluate_fixture(fixture, ast_parser=ast_parser) for fixture in fixtures)
    return RetrievalSanityEvaluation(results)


def _evaluate_fixture(
    fixture: Mapping[str, object],
    *,
    ast_parser: AstParserPort | None,
) -> dict[str, object]:
    policy = _policy_from_fixture(fixture)
    text = str(fixture["text"])
    source = SourceRecord.from_bytes(
        text.encode("utf-8"),
        source_kind=str(fixture.get("source_kind", "text")),
        location=str(fixture.get("fixture_id", "")) or None,
    )
    strategies = tuple(str(item) for item in fixture.get("strategies", ()))
    expected_terms = tuple(str(item).lower() for item in fixture.get("expected_terms", ()))
    relevant_spans = _relevant_spans(fixture)
    strategy_results = [
        _evaluate_strategy(
            strategy,
            source,
            policy,
            query=str(fixture.get("query", "")),
            expected_terms=expected_terms,
            relevant_spans=relevant_spans,
            ast_parser=ast_parser,
        )
        for strategy in strategies
    ]
    return {
        "fixture_id": fixture["fixture_id"],
        "source_family": fixture["source_family"],
        "query": fixture.get("query", ""),
        "expected_terms": list(expected_terms),
        "heldout_relevance": {
            "expected_source_spans": [
                {"start_char": start, "end_char": end} for start, end in relevant_spans
            ],
            "expected_relevant_terms": list(
                str(item).lower()
                for item in fixture.get("expected_relevant_terms", expected_terms)
            ),
        },
        "strategy_results": strategy_results,
    }


def _evaluate_strategy(
    strategy: str,
    source: SourceRecord,
    policy: SelectionPolicy,
    *,
    query: str,
    expected_terms: tuple[str, ...],
    relevant_spans: tuple[tuple[int, int], ...],
    ast_parser: AstParserPort | None,
) -> dict[str, object]:
    candidate_set, evidence = _candidate_set_for_strategy(strategy, source, policy, ast_parser)
    invariant_results = _invariant_results(source, evidence, candidate_set, policy)
    matched_terms, missing_terms, best_candidate_id = _term_coverage(candidate_set, expected_terms)
    retrieval_metrics = _retrieval_metrics(
        candidate_set,
        query=query,
        relevant_spans=relevant_spans,
        expected_terms=expected_terms,
    )
    return {
        "strategy": strategy,
        "candidate_set_id": candidate_set.candidate_set_id,
        "available": bool(candidate_set.candidates),
        "hard_invariants": [result.to_dict() for result in invariant_results],
        "hard_invariants_passed": bool(candidate_set.candidates)
        and all(result.passed for result in invariant_results),
        "retrieval_quality": {
            "answer_context_adequacy": _adequacy(matched_terms, expected_terms),
            "matched_expected_terms": list(matched_terms),
            "missing_expected_terms": list(missing_terms),
            "best_candidate_id": best_candidate_id,
        },
        "retrieval_metrics": retrieval_metrics,
        "cost": {
            "chunk_count": len(candidate_set.candidates),
            "token_total": sum(candidate.token_count for candidate in candidate_set.candidates),
            "latency_relative_units": len(candidate_set.candidates) + len(candidate_set.repairs),
        },
    }


def _candidate_set_for_strategy(
    strategy: str,
    source: SourceRecord,
    policy: SelectionPolicy,
    ast_parser: AstParserPort | None,
) -> tuple[ChunkCandidateSet, EvidenceSet]:
    if strategy == "ast_code":
        if ast_parser is None:
            return _unavailable_set(source, strategy, "ast parser port was not supplied"), EvidenceSet(
                source.source_id,
                (),
            )
        parsed = ast_parser.parse(source, "python")
        return AstCodeStrategy().form(source, parsed.evidence, policy), parsed.evidence

    evidence = observe_source(source)
    if strategy == "semantic_refinement":
        semantic = SemanticShiftInstrument().observe(source)
        evidence = EvidenceSet(evidence.source_id, (*evidence.observations, *semantic))

    paragraph = ParagraphGroupStrategy().form(source, evidence, policy)
    if strategy == "paragraph_group":
        return paragraph, evidence
    if strategy == "dynamic_token_sizing":
        dynamic_policy = SelectionPolicy(
            hard_max_tokens=policy.hard_max_tokens,
            target_tokens=max(1, min(policy.target_tokens, policy.hard_max_tokens)),
        )
        dynamic = ParagraphGroupStrategy().form(source, evidence, dynamic_policy)
        return _rename_candidate_set(dynamic, "dynamic_token_sizing"), evidence
    if strategy == "recursive_fallback":
        return RecursiveFallbackStrategy().form(
            source,
            evidence,
            policy,
            failed_candidate_set_id=paragraph.candidate_set_id,
        ), evidence
    if strategy == "hierarchical":
        return HierarchicalStrategy().form(source, evidence, policy), evidence
    if strategy == "semantic_refinement":
        semantic_policy = SelectionPolicy(
            hard_max_tokens=policy.hard_max_tokens,
            target_tokens=policy.target_tokens,
            allow_semantic_refinement=True,
        )
        return SemanticRefinementStrategy().form(
            source,
            evidence,
            semantic_policy,
            structural_candidate_set=paragraph,
        ), evidence
    return _unavailable_set(source, strategy, "unknown strategy"), evidence


def _invariant_results(
    source: SourceRecord,
    evidence: EvidenceSet,
    candidate_set: ChunkCandidateSet,
    policy: SelectionPolicy,
) -> tuple[Any, ...]:
    required = _required_spans(evidence, candidate_set)
    spans = tuple(span for candidate in candidate_set.candidates for span in candidate.spans)
    return (
        check_source_coverage(required_spans=required, chunks=candidate_set.candidates),
        check_source_lineage(candidate_set.candidates),
        check_offset_reversibility(source, spans),
        check_token_budget(candidate_set.candidates, policy.hard_max_tokens),
    )


def _required_spans(evidence: EvidenceSet, candidate_set: ChunkCandidateSet) -> tuple[SourceSpan, ...]:
    code = evidence.by_kind("code_class") + evidence.by_kind("code_function")
    if code:
        return tuple(observation.span for observation in code)
    paragraphs = evidence.by_kind("paragraph")
    if paragraphs:
        return tuple(observation.span for observation in paragraphs)
    return tuple(span for candidate in candidate_set.candidates for span in candidate.spans)


def _term_coverage(
    candidate_set: ChunkCandidateSet,
    expected_terms: tuple[str, ...],
) -> tuple[tuple[str, ...], tuple[str, ...], str | None]:
    best: tuple[str, ...] = ()
    best_candidate_id: str | None = None
    for candidate in candidate_set.candidates:
        text = candidate.text.lower()
        matched = tuple(term for term in expected_terms if term in text)
        if len(matched) > len(best):
            best = matched
            best_candidate_id = candidate.candidate_id
    missing = tuple(term for term in expected_terms if term not in best)
    return best, missing, best_candidate_id


def _retrieval_metrics(
    candidate_set: ChunkCandidateSet,
    *,
    query: str,
    relevant_spans: tuple[tuple[int, int], ...],
    expected_terms: tuple[str, ...],
) -> dict[str, object]:
    query_terms = _lexical_terms(query)
    ranking = _rank_candidates(candidate_set, query_terms, relevant_spans, expected_terms)
    relevant_count = sum(1 for item in ranking if item["relevant"])
    metrics: dict[str, object] = {
        "ranking_method": "lexical_query_overlap.v1",
        "query_terms": list(query_terms),
        "relevant_candidate_count": relevant_count,
        "ranked_candidate_ids": [str(item["candidate_id"]) for item in ranking],
        "relevant_candidate_ids": [
            str(item["candidate_id"]) for item in ranking if item["relevant"]
        ],
        "ranking": ranking,
        "mrr": _mean_reciprocal_rank(ranking),
    }
    for limit in _RECALL_KS:
        metrics[f"recall_at_{limit}"] = _recall_at(ranking, relevant_count, limit)
    return metrics


def _rank_candidates(
    candidate_set: ChunkCandidateSet,
    query_terms: tuple[str, ...],
    relevant_spans: tuple[tuple[int, int], ...],
    expected_terms: tuple[str, ...],
) -> list[dict[str, object]]:
    rows = [
        {
            "candidate_id": candidate.candidate_id,
            "score": _lexical_score(query_terms, candidate.text),
            "token_count": candidate.token_count,
            "relevant": _is_relevant(candidate, relevant_spans, expected_terms),
        }
        for candidate in candidate_set.candidates
    ]
    rows.sort(
        key=lambda item: (
            -int(item["score"]),
            int(item["token_count"]),
            str(item["candidate_id"]),
        )
    )
    return rows


def _lexical_score(query_terms: tuple[str, ...], text: str) -> int:
    text_terms = set(_lexical_terms(text))
    return sum(1 for term in dict.fromkeys(query_terms) if term in text_terms)


def _lexical_terms(text: str) -> tuple[str, ...]:
    return tuple(match.group(0).lower() for match in _LEXICAL_TOKEN_RE.finditer(text))


def _is_relevant(
    candidate: Any,
    relevant_spans: tuple[tuple[int, int], ...],
    expected_terms: tuple[str, ...],
) -> bool:
    if relevant_spans:
        return any(
            span.end_char > start and span.start_char < end
            for span in candidate.spans
            for start, end in relevant_spans
        )
    lowered = candidate.text.lower()
    return bool(expected_terms) and any(term in lowered for term in expected_terms)


def _mean_reciprocal_rank(ranking: list[dict[str, object]]) -> float:
    for index, item in enumerate(ranking, start=1):
        if item["relevant"]:
            return round(1 / index, 6)
    return 0.0


def _recall_at(
    ranking: list[dict[str, object]],
    relevant_count: int,
    limit: int,
) -> float:
    if relevant_count == 0:
        return 0.0
    recovered = sum(1 for item in ranking[:limit] if item["relevant"])
    return round(recovered / relevant_count, 6)


def _relevant_spans(fixture: Mapping[str, object]) -> tuple[tuple[int, int], ...]:
    raw = fixture.get("relevant_source_spans", ())
    spans: list[tuple[int, int]] = []
    if not isinstance(raw, list):
        return ()
    for item in raw:
        if not isinstance(item, Mapping):
            continue
        start = int(item["start_char"])
        end = int(item["end_char"])
        if end > start:
            spans.append((start, end))
    return tuple(spans)


def _adequacy(matched_terms: tuple[str, ...], expected_terms: tuple[str, ...]) -> float:
    if not expected_terms:
        return 1.0
    return round(len(matched_terms) / len(expected_terms), 6)


def _policy_from_fixture(fixture: Mapping[str, object]) -> SelectionPolicy:
    raw = fixture.get("policy", {})
    policy = raw if isinstance(raw, Mapping) else {}
    return SelectionPolicy(
        hard_max_tokens=int(policy.get("hard_max_tokens", 1200)),
        target_tokens=int(policy.get("target_tokens", 650)),
        allow_semantic_refinement=bool(policy.get("allow_semantic_refinement", False)),
    )


def _rename_candidate_set(candidate_set: ChunkCandidateSet, strategy: str) -> ChunkCandidateSet:
    return ChunkCandidateSet(
        candidate_set_id=f"{candidate_set.candidate_set_id}_{strategy}",
        strategy=strategy,
        source_id=candidate_set.source_id,
        candidates=candidate_set.candidates,
        reasons=candidate_set.reasons,
        warnings=candidate_set.warnings,
        repairs=candidate_set.repairs,
    )


def _unavailable_set(source: SourceRecord, strategy: str, reason: str) -> ChunkCandidateSet:
    return ChunkCandidateSet(
        candidate_set_id=f"candset_{source.source_id}_{strategy}_unavailable",
        strategy=strategy,
        source_id=source.source_id,
        candidates=(),
        reasons=(),
        warnings=(reason,),
    )
