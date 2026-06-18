"""Code AST observation contract."""

from __future__ import annotations

from typing import Protocol

from catalyst.observation.evidence.observation import Observation
from catalyst.source.records.source_record import SourceRecord


class CodeAstInstrument(Protocol):
    """Contract for AST-backed code observations."""

    name: str

    def observe(self, source: SourceRecord, language: str) -> tuple[Observation, ...]:
        """Observe syntax evidence without admitting code chunks."""
