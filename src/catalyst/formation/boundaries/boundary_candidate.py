"""Boundary candidate."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.formation.boundaries.boundary_score import BoundaryScore


@dataclass(frozen=True)
class BoundaryCandidate:
    """A proposed boundary before chunk admission."""

    boundary_id: str
    source_id: str
    position: int
    score: BoundaryScore
    accepted: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "boundary_id": self.boundary_id,
            "source_id": self.source_id,
            "position": self.position,
            "accepted": self.accepted,
            "score": self.score.value,
            "evidence": list(self.score.evidence_ids),
            "penalties": list(self.score.penalties),
        }
