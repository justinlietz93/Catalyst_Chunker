"""Optional telemetry boundary adapters."""

from catalyst.boundary.adapters.telemetry.memory import (
    InMemoryTelemetrySink,
    NoOpTelemetrySink,
    TelemetryRecord,
    record_telemetry,
)

__all__ = [
    "InMemoryTelemetrySink",
    "NoOpTelemetrySink",
    "TelemetryRecord",
    "record_telemetry",
]
