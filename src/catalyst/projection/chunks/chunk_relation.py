"""Chunk relation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChunkRelation:
    """A relation between admitted chunks."""

    source_chunk_id: str
    target_chunk_id: str
    relation_kind: str
    evidence_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "source_chunk_id": self.source_chunk_id,
            "target_chunk_id": self.target_chunk_id,
            "relation_kind": self.relation_kind,
            "evidence_ids": list(self.evidence_ids),
        }
