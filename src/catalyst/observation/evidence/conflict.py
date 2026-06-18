"""Observation conflict record."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Conflict:
    """A disagreement between observations."""

    conflict_id: str
    observation_ids: tuple[str, ...]
    reason: str
