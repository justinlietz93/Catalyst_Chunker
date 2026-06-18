"""Evaluate relation-window context recovery without changing indexed chunks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.observation.instruments.tokenizer_instrument import count_tokens
from catalyst.operation.commands.chunk_source import ChunkSourceResult, chunk_source
from catalyst.projection.schemas.schema_version import CONTEXT_RECOVERY_BENCHMARK_SCHEMA_VERSION
from catalyst.projection.views.sentence_window_view import SentenceWindowProjection


@dataclass(frozen=True)
class ContextRecoveryBenchmark:
    """Diagnostic benchmark for relation-based retrieval context recovery."""

    result: ChunkSourceResult
    expected_terms: tuple[str, ...]
    sentence_window_records: tuple[dict[str, object], ...]

    def record(self) -> dict[str, object]:
        indexed_quality = _best_quality(
            self.sentence_window_records,
            self.expected_terms,
            include_recovered_context=False,
        )
        relation_quality = _best_quality(
            self.sentence_window_records,
            self.expected_terms,
            include_recovered_context=True,
        )
        return {
            "schema_version": CONTEXT_RECOVERY_BENCHMARK_SCHEMA_VERSION,
            "projection_kind": "context_recovery_benchmark",
            "source_id": self.result.source.source_id,
            "authority": {
                "diagnostic_only": True,
                "does_not_admit_chunks": True,
                "indexed_text_unchanged": True,
            },
            "index_cost": {
                "chunk_count": len(self.result.graph.chunks),
                "indexed_token_total": sum(
                    chunk.token_count for chunk in self.result.graph.chunks
                ),
                "relation_count": len(self.result.graph.relations),
            },
            "context_recovery": {
                "projection_kind": "sentence_window",
                "relation_window_token_total": _relation_window_token_total(
                    self.sentence_window_records
                ),
            },
            "retrieval_quality": {
                "indexed_only": indexed_quality,
                "relation_window": relation_quality,
            },
        }


def evaluate_context_recovery(
    raw_bytes: bytes,
    *,
    expected_terms: tuple[str, ...],
    location: str | None = None,
    policy: SelectionPolicy | None = None,
) -> ContextRecoveryBenchmark:
    """Measure relation-window recovery against indexed-only chunk text."""

    result = chunk_source(raw_bytes, location=location, policy=policy)
    sentence_windows = tuple(SentenceWindowProjection(result.graph).records())
    return ContextRecoveryBenchmark(
        result=result,
        expected_terms=tuple(term.lower() for term in expected_terms),
        sentence_window_records=sentence_windows,
    )


def _best_quality(
    records: tuple[dict[str, object], ...],
    expected_terms: tuple[str, ...],
    *,
    include_recovered_context: bool,
) -> dict[str, object]:
    best_terms: tuple[str, ...] = ()
    best_chunk_id: str | None = None
    for record in records:
        text = str(record["indexed_text"])
        if include_recovered_context:
            text = f"{text}\n{_context_text(record['recovered_context'])}"
        lowered = text.lower()
        matched = tuple(term for term in expected_terms if term in lowered)
        if len(matched) > len(best_terms):
            best_terms = matched
            best_chunk_id = str(record["chunk_id"])
    missing = tuple(term for term in expected_terms if term not in best_terms)
    return {
        "answer_context_adequacy": _adequacy(best_terms, expected_terms),
        "matched_expected_terms": list(best_terms),
        "missing_expected_terms": list(missing),
        "best_chunk_id": best_chunk_id,
    }


def _relation_window_token_total(records: tuple[dict[str, object], ...]) -> int:
    return sum(count_tokens(_context_text(record["recovered_context"])) for record in records)


def _context_text(context: Any) -> str:
    if not isinstance(context, dict):
        return ""
    values: list[str] = []
    for key in ("previous", "next"):
        raw = context.get(key, ())
        if isinstance(raw, list):
            values.extend(str(item) for item in raw)
    return "\n".join(values)


def _adequacy(matched_terms: tuple[str, ...], expected_terms: tuple[str, ...]) -> float:
    if not expected_terms:
        return 1.0
    return round(len(matched_terms) / len(expected_terms), 6)
