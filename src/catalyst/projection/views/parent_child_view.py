"""Parent/child projection."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.projection.chunks.chunk_graph import ChunkGraph
from catalyst.projection.schemas.schema_version import PARENT_CHILD_SCHEMA_VERSION


@dataclass(frozen=True)
class ParentChildProjection:
    """Versioned parent/child context view."""

    graph: ChunkGraph

    def record(self) -> dict[str, object]:
        children = [
            {
                "chunk_id": chunk.chunk_id,
                "source_id": chunk.source_id,
                "token_count": chunk.token_count,
                "source_spans": [span.to_dict() for span in chunk.spans],
            }
            for chunk in self.graph.chunks
        ]
        return {
            "schema_version": PARENT_CHILD_SCHEMA_VERSION,
            "projection_kind": "parent_child",
            "source_id": self.graph.source_id,
            "parent": {
                "parent_id": f"parent_{self.graph.source_id}",
                "child_count": len(children),
            },
            "children": children,
            "warnings": [],
            "omissions": [],
        }
