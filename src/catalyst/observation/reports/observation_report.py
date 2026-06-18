"""Observation report."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.observation.evidence.evidence_set import EvidenceSet


@dataclass(frozen=True)
class ObservationReport:
    """Summary of evidence emitted for one source."""

    evidence: EvidenceSet
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "evidence": self.evidence.to_dict(),
            "warnings": list(self.warnings),
        }
