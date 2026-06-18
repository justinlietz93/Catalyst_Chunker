"""PDF layout observation contract."""

from __future__ import annotations

from typing import Protocol

from catalyst.observation.evidence.observation import Observation
from catalyst.source.records.source_record import SourceRecord


class PdfLayoutInstrument(Protocol):
    """Contract for PDF layout observations from boundary adapters."""

    name: str

    def observe(self, source: SourceRecord) -> tuple[Observation, ...]:
        """Observe page, block, header, footer, and table layout evidence."""
