"""Candidate reason."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CandidateReason:
    """Why a chunk candidate exists."""

    reason_id: str
    kind: str
    evidence_ids: tuple[str, ...]
    description: str

    def to_dict(self) -> dict[str, object]:
        return {
            "reason_id": self.reason_id,
            "kind": self.kind,
            "evidence_ids": list(self.evidence_ids),
            "description": self.description,
        }
