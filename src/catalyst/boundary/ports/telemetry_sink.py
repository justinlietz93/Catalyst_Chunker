"""Telemetry boundary port."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class TelemetrySink(Protocol):
    """Boundary port for telemetry."""

    def record(self, event_name: str, payload: dict[str, object]) -> None:
        """Record a telemetry event."""
