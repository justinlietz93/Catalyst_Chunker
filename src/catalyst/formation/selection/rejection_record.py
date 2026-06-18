"""Candidate rejection record."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.source.records.source_span import SourceSpan


@dataclass(frozen=True)
class RejectionRecord:
    """Inspectable rejection for a candidate or candidate set."""

    rejection_id: str
    rejected_id: str
    reason: str
    evidence_ids: tuple[str, ...] = ()
    source_spans: tuple[SourceSpan, ...] = ()
    reconsideration_trigger: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "rejection_id": self.rejection_id,
            "rejected_id": self.rejected_id,
            "reason": self.reason,
            "evidence_ids": list(self.evidence_ids),
            "source_spans": [span.to_dict() for span in self.source_spans],
            "reconsideration_trigger": self.reconsideration_trigger,
        }
