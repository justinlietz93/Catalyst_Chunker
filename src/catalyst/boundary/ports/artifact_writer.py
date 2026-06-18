"""Artifact writing port."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Protocol


class ArtifactWriter(Protocol):
    """Boundary port for writing projection records."""

    def write_records(self, location: str, records: Iterable[Mapping[str, object]]) -> None:
        """Write projection records to a location."""

    def write_record(self, location: str, record: Mapping[str, object]) -> None:
        """Write one projection record to a location."""
