"""Stable telemetry event names and payload field declarations."""

from __future__ import annotations

CHUNK_SOURCE_COMPLETED = "catalyst.chunk_source.completed"
CHUNK_SOURCE_FAILED = "catalyst.chunk_source.failed"
INVARIANT_VIOLATION_RECORDED = "catalyst.invariant.violation_recorded"
ADAPTER_FAILURE_RECORDED = "catalyst.adapter.failure_recorded"
PERFORMANCE_BENCHMARK_COMPLETED = "catalyst.performance_benchmark.completed"

TELEMETRY_EVENT_NAMES = (
    CHUNK_SOURCE_COMPLETED,
    CHUNK_SOURCE_FAILED,
    INVARIANT_VIOLATION_RECORDED,
    ADAPTER_FAILURE_RECORDED,
    PERFORMANCE_BENCHMARK_COMPLETED,
)

TELEMETRY_EVENT_PAYLOAD_FIELDS = {
    CHUNK_SOURCE_COMPLETED: (
        "source_id",
        "chunk_count",
        "token_total",
        "invariant_passed",
        "elapsed_nanoseconds",
    ),
    CHUNK_SOURCE_FAILED: (
        "source_id",
        "error_code",
        "error_type",
        "elapsed_nanoseconds",
    ),
    INVARIANT_VIOLATION_RECORDED: (
        "source_id",
        "invariant_id",
        "result_id",
        "violation_count",
    ),
    ADAPTER_FAILURE_RECORDED: (
        "adapter_name",
        "port_name",
        "error_type",
        "error_code",
    ),
    PERFORMANCE_BENCHMARK_COMPLETED: (
        "fixture_id",
        "source_family",
        "strategy",
        "elapsed_nanoseconds",
        "peak_memory_bytes",
        "chunk_count",
        "token_total",
    ),
}


def telemetry_payload_fields(event_name: str) -> tuple[str, ...]:
    """Return the documented payload fields for one telemetry event."""

    return tuple(TELEMETRY_EVENT_PAYLOAD_FIELDS.get(event_name, ()))
