"""Emit versioned projections from operation results."""

from __future__ import annotations

from catalyst.operation.commands.chunk_source import ChunkSourceResult
from catalyst.projection.views.audit_view import AuditProjection
from catalyst.projection.views.boundary_inspection_view import BoundaryInspectionProjection
from catalyst.projection.views.parent_child_view import ParentChildProjection
from catalyst.projection.views.retrieval_view import RetrievalProjection
from catalyst.projection.views.sentence_window_view import SentenceWindowProjection


def emit_projection(result: ChunkSourceResult, projection_kind: str) -> dict[str, object] | list[dict[str, object]]:
    """Render a supported projection from a chunk source result."""

    if projection_kind == "retrieval":
        return RetrievalProjection(result.graph).records()
    if projection_kind == "audit":
        return AuditProjection(
            graph=result.graph,
            invariant_ledger=result.invariant_ledger,
            accepted_candidate_set_id=result.selection.accepted.candidate_set_id,
            accepted_candidate_set=result.selection.accepted,
            rejections=result.selection.rejections,
            repairs=result.selection.accepted.repairs,
            evidence=result.evidence,
        ).record()
    if projection_kind == "parent_child":
        return ParentChildProjection(result.graph).record()
    if projection_kind == "sentence_window":
        return SentenceWindowProjection(result.graph).records()
    raise ValueError(f"unsupported projection kind: {projection_kind}")


def emit_boundary_inspection(
    *,
    source_id: str,
    boundary_candidates: tuple[object, ...],
    rejections: tuple[object, ...] = (),
) -> dict[str, object]:
    """Render a boundary inspection projection."""

    return BoundaryInspectionProjection(
        source_id=source_id,
        boundary_candidates=boundary_candidates,
        rejections=rejections,
    ).record()
