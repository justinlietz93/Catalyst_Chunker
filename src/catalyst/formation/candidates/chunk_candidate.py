"""Chunk candidate."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.formation.candidates.candidate_metrics import CandidateMetrics
from catalyst.source.records.source_span import SourceSpan


@dataclass(frozen=True)
class ChunkCandidate:
    """A proposed chunk before admission."""

    candidate_id: str
    source_id: str
    spans: tuple[SourceSpan, ...]
    text: str
    token_count: int
    evidence_ids: tuple[str, ...]
    reason_ids: tuple[str, ...]
    metrics: CandidateMetrics
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "candidate_id": self.candidate_id,
            "source_id": self.source_id,
            "spans": [span.to_dict() for span in self.spans],
            "text": self.text,
            "token_count": self.token_count,
            "evidence_ids": list(self.evidence_ids),
            "reason_ids": list(self.reason_ids),
            "metrics": self.metrics.to_dict(),
            "warnings": list(self.warnings),
        }
