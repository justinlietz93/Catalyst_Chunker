"""Boundary score."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BoundaryScore:
    """Score for a proposed boundary."""

    value: float
    evidence_ids: tuple[str, ...] = ()
    penalties: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0 <= self.value <= 1:
            raise ValueError("boundary score must be between 0 and 1")
