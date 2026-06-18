from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.operation.commands.chunk_source import chunk_source
from catalyst.projection.views.audit_view import AuditProjection
from catalyst.projection.views.retrieval_view import RetrievalProjection
from catalyst.shared.errors import EmptySourceError


def test_chunk_source_forms_lineage_preserving_graph() -> None:
    result = chunk_source(
        b"# Title\n\nFirst paragraph has source structure.\n\nSecond paragraph continues it.",
        location="fixture.md",
    )

    assert result.graph.chunks
    assert result.invariant_ledger.passed
    assert {item.invariant_id for item in result.invariant_ledger.results} >= {"I001", "I002", "I003"}
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


def test_chunk_source_rejects_empty_source_with_typed_error() -> None:
    for raw in (b"", b"   ", b"\n\n"):
        try:
            chunk_source(raw)
        except EmptySourceError as error:
            assert "source contains no chunkable text" in str(error)
        else:
            raise AssertionError("empty source should not admit a chunk graph")


def test_long_atomic_text_is_one_baseline_token_not_character_split() -> None:
    result = chunk_source(
        b"a" * 5000,
        policy=SelectionPolicy(target_tokens=1, hard_max_tokens=1),
    )

    assert result.invariant_ledger.passed
    assert len(result.graph.chunks) == 1
    assert result.graph.chunks[0].token_count == 1
    assert result.graph.chunks[0].text == "a" * 5000
