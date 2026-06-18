"""Retrieval projection."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.projection.chunks.chunk_graph import ChunkGraph
from catalyst.projection.schemas.schema_version import RETRIEVAL_SCHEMA_VERSION


@dataclass(frozen=True)
class RetrievalProjection:
    """Versioned retrieval records."""

    graph: ChunkGraph

    def records(self) -> list[dict[str, object]]:
        return [
            {
                "schema_version": RETRIEVAL_SCHEMA_VERSION,
                "projection_kind": "retrieval",
                "chunk_id": chunk.chunk_id,
                "source_id": chunk.source_id,
                "text": chunk.text,
                "token_count": chunk.token_count,
                "source_spans": [span.to_dict() for span in chunk.spans],
                "relations": self._relations_for(chunk.chunk_id),
                "warnings": list(chunk.warning_ids),
                "omissions": [],
            }
            for chunk in self.graph.chunks
        ]

    def _relations_for(self, chunk_id: str) -> dict[str, str]:
        relations: dict[str, str] = {}
        for relation in self.graph.relations:
            if relation.source_chunk_id == chunk_id:
                relations[relation.relation_kind] = relation.target_chunk_id
        return relations
