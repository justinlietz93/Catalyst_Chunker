"""Chunk graph."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.projection.chunks.accepted_chunk import AcceptedChunk
from catalyst.projection.chunks.chunk_relation import ChunkRelation


@dataclass(frozen=True)
class ChunkGraph:
    """Admitted graph of chunks and relations."""

    graph_id: str
    source_id: str
    chunks: tuple[AcceptedChunk, ...]
    relations: tuple[ChunkRelation, ...]
    formation_policy_id: str
    invariant_result_ids: tuple[str, ...]
    decision_record_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "graph_id": self.graph_id,
            "source_id": self.source_id,
            "chunks": [chunk.to_dict() for chunk in self.chunks],
            "relations": [relation.to_dict() for relation in self.relations],
            "formation_policy_id": self.formation_policy_id,
            "invariant_result_ids": list(self.invariant_result_ids),
            "decision_record_ids": list(self.decision_record_ids),
        }
