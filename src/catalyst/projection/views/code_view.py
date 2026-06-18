"""Code projection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from catalyst.projection.chunks.chunk_graph import ChunkGraph


@dataclass(frozen=True)
class CodeProjection:
    """Versioned code view with admitted AST evidence."""

    graph: ChunkGraph
    parsed: Any

    def record(self) -> dict[str, object]:
        return {
            "schema_version": "catalyst.code.v1",
            "projection_kind": "code",
            "source_id": self.graph.source_id,
            "language": self.parsed.language,
            "chunks": [self._chunk_record(chunk) for chunk in self.graph.chunks],
            "relations": [relation.to_dict() for relation in self.graph.relations],
            "warnings": list(self.parsed.warnings),
            "omissions": [],
        }

    def _chunk_record(self, chunk) -> dict[str, object]:
        evidence = [
            observation
            for observation in self.parsed.evidence.observations
            if observation.observation_id in chunk.evidence_ids
        ]
        return {
            "chunk_id": chunk.chunk_id,
            "source_id": chunk.source_id,
            "text": chunk.text,
            "token_count": chunk.token_count,
            "source_spans": [span.to_dict() for span in chunk.spans],
            "definitions": _payload_values(evidence, {"code_class", "code_function"}, "name"),
            "imports": _payload_values(self.parsed.evidence.by_kind("code_import"), {"code_import"}, "module"),
            "calls": _payload_values(evidence, {"code_call"}, "call"),
            "warnings": list(chunk.warning_ids),
        }


def _payload_values(observations, kinds: set[str], key: str) -> list[object]:
    values = []
    for observation in observations:
        if observation.kind in kinds and observation.payload.get(key):
            values.append(observation.payload[key])
    return values
