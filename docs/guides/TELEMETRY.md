# Telemetry

Telemetry is optional boundary observation. It does not admit chunks, reject chunks, or override invariants.

## Event Names

Stable event names are declared in `catalyst.boundary.ports.telemetry_events`:

- `catalyst.chunk_source.completed`
- `catalyst.chunk_source.failed`
- `catalyst.invariant.violation_recorded`
- `catalyst.adapter.failure_recorded`
- `catalyst.performance_benchmark.completed`

The `TELEMETRY_EVENT_PAYLOAD_FIELDS` mapping documents the expected payload fields for each event. Default payload fields identify source IDs, counts, invariant IDs, elapsed time, peak memory, adapter names, and error codes. They do not include full source text.

## Adapters

Catalyst includes no-dependency telemetry adapters:

```python
from catalyst.boundary.adapters.telemetry import (
    InMemoryTelemetrySink,
    NoOpTelemetrySink,
    record_telemetry,
)
from catalyst.boundary.ports import CHUNK_SOURCE_COMPLETED

sink = InMemoryTelemetrySink()
record_telemetry(
    sink,
    CHUNK_SOURCE_COMPLETED,
    {
        "source_id": "src_123",
        "chunk_count": 3,
        "token_total": 120,
        "invariant_passed": True,
        "elapsed_nanoseconds": 1000,
    },
)
```

`record_telemetry` returns `False` if a sink fails and `strict=False`. Pass `strict=True` when an embedding application wants telemetry failures to be fatal.

## Optional External Systems

Prometheus, OpenTelemetry, log drains, or hosted tracing systems should be implemented as optional boundary adapters. They should not become required runtime dependencies.
