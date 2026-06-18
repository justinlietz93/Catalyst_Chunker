"""Provenance record."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Provenance:
    """A concise statement of source origin."""

    source_id: str
    location: str | None
    source_kind: str
