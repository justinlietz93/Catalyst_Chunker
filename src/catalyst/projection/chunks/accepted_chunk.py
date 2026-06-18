"""Accepted chunk."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.source.records.source_span import SourceSpan


@dataclass(frozen=True)
class AcceptedChunk:
    """A chunk admitted after evidence and invariant checks."""

    chunk_id: str
    source_id: str
    spans: tuple[SourceSpan, ...]
    text: str
    token_count: int
    chunk_kind: str
    candidate_set_id: str
    evidence_ids: tuple[str, ...]
    warning_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "chunk_id": self.chunk_id,
            "source_id": self.source_id,
            "spans": [span.to_dict() for span in self.spans],
            "text": self.text,
            "token_count": self.token_count,
            "chunk_kind": self.chunk_kind,
            "candidate_set_id": self.candidate_set_id,
            "evidence_ids": list(self.evidence_ids),
            "warning_ids": list(self.warning_ids),
        }
