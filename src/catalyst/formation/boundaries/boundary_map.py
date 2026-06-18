"""Boundary map."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.formation.boundaries.boundary_candidate import BoundaryCandidate


@dataclass(frozen=True)
class BoundaryMap:
    """Inspectable boundary candidates for one source."""

    source_id: str
    boundaries: tuple[BoundaryCandidate, ...]

    def accepted(self) -> tuple[BoundaryCandidate, ...]:
        return tuple(boundary for boundary in self.boundaries if boundary.accepted)

    def to_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "boundaries": [boundary.to_dict() for boundary in self.boundaries],
        }
