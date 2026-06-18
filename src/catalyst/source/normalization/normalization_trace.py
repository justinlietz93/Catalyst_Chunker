"""Normalization trace records."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NormalizationTrace:
    """Records whether canonical text can be traced to raw source."""

    trace_id: str
    source_id: str
    reversible: bool
    lossy: bool
    notes: tuple[str, ...] = ()
