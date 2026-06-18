"""Candidate set."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.formation.candidates.candidate_reason import CandidateReason
from catalyst.formation.candidates.chunk_candidate import ChunkCandidate
from catalyst.formation.repair.repair_record import RepairRecord


@dataclass(frozen=True)
class ChunkCandidateSet:
    """Candidates formed by one strategy."""

    candidate_set_id: str
    strategy: str
    source_id: str
    candidates: tuple[ChunkCandidate, ...]
    reasons: tuple[CandidateReason, ...]
    warnings: tuple[str, ...] = ()
    repairs: tuple[RepairRecord, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "candidate_set_id": self.candidate_set_id,
            "strategy": self.strategy,
            "source_id": self.source_id,
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "reasons": [reason.to_dict() for reason in self.reasons],
            "warnings": list(self.warnings),
            "repairs": [repair.to_dict() for repair in self.repairs],
        }
