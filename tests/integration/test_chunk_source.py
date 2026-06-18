from catalyst.operation.commands.chunk_source import chunk_source
from catalyst.projection.views.audit_view import AuditProjection
from catalyst.projection.views.retrieval_view import RetrievalProjection


def test_chunk_source_forms_lineage_preserving_graph() -> None:
    result = chunk_source(
        b"# Title\n\nFirst paragraph has source structure.\n\nSecond paragraph continues it.",
        location="fixture.md",
    )

    assert result.graph.chunks
    assert result.invariant_ledger.passed
    assert all(chunk.source_id == result.source.source_id for chunk in result.graph.chunks)
    assert all(chunk.spans for chunk in result.graph.chunks)

    retrieval = RetrievalProjection(result.graph).records()
    audit = AuditProjection(
        graph=result.graph,
        invariant_ledger=result.invariant_ledger,
        accepted_candidate_set_id=result.selection.accepted.candidate_set_id,
        rejections=result.selection.rejections,
    ).record()

    assert retrieval[0]["schema_version"] == "catalyst.retrieval.v1"
    assert audit["schema_version"] == "catalyst.audit.v1"
    assert audit["rejections"] == []
