"""Candidate metrics."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CandidateMetrics:
    """Lightweight candidate quality metrics."""

    token_count: int
    boundary_count: int
    orphan_count: int = 0
    repair_count: int = 0

    def to_dict(self) -> dict[str, object]:
        return {
            "token_count": self.token_count,
            "boundary_count": self.boundary_count,
            "orphan_count": self.orphan_count,
            "repair_count": self.repair_count,
        }
