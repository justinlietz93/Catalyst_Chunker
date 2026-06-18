"""No-dependency telemetry adapters."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.boundary.ports.telemetry_sink import TelemetrySink


@dataclass(frozen=True)
class TelemetryRecord:
    """Recorded telemetry event for local tests and embedding applications."""

    event_name: str
    payload: dict[str, object]


class NoOpTelemetrySink:
    """Telemetry sink that intentionally records nothing."""

    def record(self, event_name: str, payload: dict[str, object]) -> None:
        return None


class InMemoryTelemetrySink:
    """Telemetry sink that stores event records in process memory."""

    def __init__(self) -> None:
        self._events: list[TelemetryRecord] = []

    @property
    def events(self) -> tuple[TelemetryRecord, ...]:
        return tuple(self._events)

    def record(self, event_name: str, payload: dict[str, object]) -> None:
        self._events.append(TelemetryRecord(event_name, dict(payload)))


def record_telemetry(
    sink: TelemetrySink | None,
    event_name: str,
    payload: dict[str, object],
    *,
    strict: bool = False,
) -> bool:
    """Record telemetry nonfatally unless strict mode is requested."""

    if sink is None:
        return False
    try:
        sink.record(event_name, payload)
    except Exception:
        if strict:
            raise
        return False
    return True
