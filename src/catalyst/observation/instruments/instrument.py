"""Observation instrument contract."""

from __future__ import annotations

from typing import Protocol

from catalyst.observation.evidence.observation import Observation
from catalyst.source.records.source_record import SourceRecord


class Instrument(Protocol):
    """Contract for source-observing instruments."""

    name: str

    def observe(self, source: SourceRecord) -> tuple[Observation, ...]:
        """Observe source material without admitting structure."""
