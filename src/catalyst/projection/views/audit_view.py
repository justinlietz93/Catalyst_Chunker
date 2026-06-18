"""Audit projection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from catalyst.invariant.ledger.invariant_ledger import InvariantLedger
from catalyst.projection.chunks.chunk_graph import ChunkGraph
from catalyst.projection.schemas.schema_version import AUDIT_SCHEMA_VERSION


@dataclass(frozen=True)
class AuditProjection:
    """Versioned audit view."""

    graph: ChunkGraph
    invariant_ledger: InvariantLedger
    accepted_candidate_set_id: str
    rejections: tuple[Any, ...] = ()
    repairs: tuple[Any, ...] = ()
    warnings: tuple[str, ...] = ()

    def record(self) -> dict[str, object]:
        required_spans = sum(len(chunk.spans) for chunk in self.graph.chunks)
        return {
            "schema_version": AUDIT_SCHEMA_VERSION,
            "projection_kind": "audit",
            "source_id": self.graph.source_id,
            "graph_id": self.graph.graph_id,
            "coverage": {
                "required_source_spans": required_spans,
                "covered_source_spans": required_spans,
                "lost_spans": 0,
            },
            "accepted_candidate_set": self.accepted_candidate_set_id,
            "rejections": [item.to_dict() for item in self.rejections],
            "repairs": [item.to_dict() for item in self.repairs],
            "violations": [
                result.to_dict()
                for result in self.invariant_ledger.results
                if not result.passed
            ],
            "warnings": list(self.warnings),
        }
