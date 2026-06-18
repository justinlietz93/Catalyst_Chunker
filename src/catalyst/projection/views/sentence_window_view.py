"""Sentence-window projection."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.projection.chunks.accepted_chunk import AcceptedChunk
from catalyst.projection.chunks.chunk_graph import ChunkGraph
from catalyst.projection.schemas.schema_version import SENTENCE_WINDOW_SCHEMA_VERSION


@dataclass(frozen=True)
class SentenceWindowProjection:
    """Versioned retrieval context recovery view."""

    graph: ChunkGraph

    def records(self) -> list[dict[str, object]]:
        by_id = {chunk.chunk_id: chunk for chunk in self.graph.chunks}
        return [
            {
                "schema_version": SENTENCE_WINDOW_SCHEMA_VERSION,
                "projection_kind": "sentence_window",
                "chunk_id": chunk.chunk_id,
                "source_id": chunk.source_id,
                "indexed_text": chunk.text,
                "recovered_context": self._context_for(chunk, by_id),
                "source_spans": [span.to_dict() for span in chunk.spans],
                "warnings": [],
                "omissions": [],
            }
            for chunk in self.graph.chunks
        ]

    def _context_for(
        self,
        chunk: AcceptedChunk,
        by_id: dict[str, AcceptedChunk],
    ) -> dict[str, object]:
        previous_text: list[str] = []
        next_text: list[str] = []
        for relation in self.graph.relations:
            if relation.source_chunk_id != chunk.chunk_id:
                continue
            related = by_id.get(relation.target_chunk_id)
            if not related:
                continue
            if relation.relation_kind in {"previous", "previous_sibling"}:
                previous_text.append(related.text)
            if relation.relation_kind in {"next", "next_sibling"}:
                next_text.append(related.text)
        return {
            "context_kind": "relation_window",
            "previous": previous_text,
            "next": next_text,
        }
