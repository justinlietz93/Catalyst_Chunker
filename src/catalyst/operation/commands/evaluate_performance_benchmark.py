"""Evaluate diagnostic performance benchmark fixtures."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from time import perf_counter_ns
import tracemalloc
from typing import Any

from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.observation.instruments.collect import observe_source
from catalyst.operation.commands.chunk_source import chunk_source
from catalyst.projection.schemas.schema_version import PERFORMANCE_BENCHMARK_SCHEMA_VERSION
from catalyst.shared.errors import CatalystError
from catalyst.source.normalization.reversible_normalizer import ReversibleNormalizer
from catalyst.source.records.source_record import SourceRecord


@dataclass(frozen=True)
class PerformanceBenchmark:
    """Diagnostic benchmark report for chunking cost and resource shape."""

    fixture_results: tuple[dict[str, object], ...]

    def record(self) -> dict[str, object]:
        return {
            "schema_version": PERFORMANCE_BENCHMARK_SCHEMA_VERSION,
            "projection_kind": "performance_benchmark",
            "authority": {
                "diagnostic_only": True,
                "not_an_admission_gate": True,
                "machine_dependent_timing": True,
            },
            "fixtures": list(self.fixture_results),
        }


def evaluate_performance_benchmark(
    fixtures: tuple[Mapping[str, object], ...],
) -> PerformanceBenchmark:
    """Measure chunking cost for benchmark fixtures without setting hard budgets."""

    results = tuple(_evaluate_fixture(fixture) for fixture in fixtures)
    return PerformanceBenchmark(results)


def _evaluate_fixture(fixture: Mapping[str, object]) -> dict[str, object]:
    text = str(fixture["text"])
    raw_bytes = text.encode("utf-8")
    source_kind = str(fixture.get("source_kind", "markdown"))
    fixture_id = str(fixture["fixture_id"])
    source = _normalized_source(raw_bytes, source_kind=source_kind, location=fixture_id)
    strategies = tuple(str(item) for item in fixture.get("strategies", ("chunk_source",)))
    return {
        "fixture_id": fixture_id,
        "source_family": fixture["source_family"],
        "source_kind": source_kind,
        "source_id": source.source_id,
        "source_measures": _source_measures(source),
        "strategy_results": [
            _evaluate_strategy(strategy, raw_bytes, source_kind, fixture_id, fixture)
            for strategy in strategies
        ],
    }


def _evaluate_strategy(
    strategy: str,
    raw_bytes: bytes,
    source_kind: str,
    location: str,
    fixture: Mapping[str, object],
) -> dict[str, object]:
    policy = _policy_from_fixture(fixture, strategy)
    if strategy not in {"chunk_source", "chunk_source_semantic_refinement"}:
        return {
            "strategy": strategy,
            "status": "failed",
            "error": {
                "code": "benchmark.strategy_unsupported",
                "message": f"unsupported benchmark strategy: {strategy}",
                "details": {},
            },
        }

    tracemalloc.start()
    started = perf_counter_ns()
    try:
        result = chunk_source(
            raw_bytes,
            location=location,
            source_kind=source_kind,
            policy=policy,
        )
        elapsed_ns = perf_counter_ns() - started
        _current_bytes, peak_bytes = tracemalloc.get_traced_memory()
    except CatalystError as error:
        elapsed_ns = perf_counter_ns() - started
        _current_bytes, peak_bytes = tracemalloc.get_traced_memory()
        return _failed_result(strategy, policy, elapsed_ns, peak_bytes, error.to_dict())
    except Exception as error:  # pragma: no cover - defensive diagnostic envelope
        elapsed_ns = perf_counter_ns() - started
        _current_bytes, peak_bytes = tracemalloc.get_traced_memory()
        return _failed_result(
            strategy,
            policy,
            elapsed_ns,
            peak_bytes,
            {
                "code": "benchmark.unexpected_error",
                "message": str(error),
                "details": {"error_type": error.__class__.__name__},
            },
        )
    finally:
        tracemalloc.stop()

    chunks = result.graph.chunks
    return {
        "strategy": strategy,
        "admitted_strategy": result.selection.accepted.strategy,
        "status": "passed",
        "policy": policy.to_dict(),
        "elapsed_time": {
            "nanoseconds": elapsed_ns,
            "seconds": round(elapsed_ns / 1_000_000_000, 9),
        },
        "memory": {
            "peak_bytes": peak_bytes,
            "measurement": "tracemalloc",
        },
        "chunk_count": len(chunks),
        "token_total": sum(chunk.token_count for chunk in chunks),
        "repair_count": _repair_count(result.selection.accepted),
        "invariant_summary": _invariant_summary(result.invariant_ledger.to_dict()),
        "selected_candidate_set_id": result.selection.accepted.candidate_set_id,
        "graph_id": result.graph.graph_id,
    }


def _failed_result(
    strategy: str,
    policy: SelectionPolicy,
    elapsed_ns: int,
    peak_bytes: int,
    error: dict[str, object],
) -> dict[str, object]:
    return {
        "strategy": strategy,
        "status": "failed",
        "policy": policy.to_dict(),
        "elapsed_time": {
            "nanoseconds": elapsed_ns,
            "seconds": round(elapsed_ns / 1_000_000_000, 9),
        },
        "memory": {
            "peak_bytes": peak_bytes,
            "measurement": "tracemalloc",
        },
        "error": error,
    }


def _source_measures(source: SourceRecord) -> dict[str, object]:
    evidence = observe_source(source)
    measures = evidence.by_kind("source_measure")
    if not measures:
        return {}
    return dict(measures[0].payload)


def _normalized_source(
    raw_bytes: bytes,
    *,
    source_kind: str,
    location: str,
) -> SourceRecord:
    source = SourceRecord.from_bytes(raw_bytes, source_kind=source_kind, location=location)
    normalized, _trace = ReversibleNormalizer().normalize(source)
    return normalized


def _policy_from_fixture(
    fixture: Mapping[str, object],
    strategy: str,
) -> SelectionPolicy:
    raw = fixture.get("policy", {})
    policy = raw if isinstance(raw, Mapping) else {}
    return SelectionPolicy(
        hard_max_tokens=int(policy.get("hard_max_tokens", 1200)),
        target_tokens=int(policy.get("target_tokens", 650)),
        allow_semantic_refinement=(
            bool(policy.get("allow_semantic_refinement", False))
            or strategy == "chunk_source_semantic_refinement"
        ),
    )


def _repair_count(candidate_set: Any) -> int:
    candidate_repairs = sum(candidate.metrics.repair_count for candidate in candidate_set.candidates)
    return candidate_repairs + len(candidate_set.repairs)


def _invariant_summary(ledger_record: dict[str, object]) -> dict[str, object]:
    results = ledger_record.get("results", ())
    result_records = results if isinstance(results, list) else []
    return {
        "passed": bool(ledger_record.get("passed", False)),
        "result_count": len(result_records),
        "invariant_ids": [str(result["invariant_id"]) for result in result_records],
        "violations": [
            result for result in result_records if not bool(result.get("passed", False))
        ],
    }
