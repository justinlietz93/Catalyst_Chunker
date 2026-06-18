"""Repair record."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RepairRecord:
    """A traceable change made to preserve admission invariants."""

    repair_id: str
    repaired_id: str
    reason: str
    evidence_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "repair_id": self.repair_id,
            "repaired_id": self.repaired_id,
            "reason": self.reason,
            "evidence_ids": list(self.evidence_ids),
        }
