from catalyst.operation.commands.chunk_source import chunk_source
from catalyst.operation.commands.emit_projection import emit_projection
from catalyst.projection.views.parent_child_view import ParentChildProjection
from catalyst.projection.views.sentence_window_view import SentenceWindowProjection


def test_parent_child_projection_is_versioned() -> None:
    result = chunk_source(b"# Title\n\nFirst paragraph.\n\nSecond paragraph.")

    record = ParentChildProjection(result.graph).record()

    assert record["schema_version"] == "catalyst.parent_child.v1"
    assert record["projection_kind"] == "parent_child"
    assert record["parent"]["child_count"] == len(result.graph.chunks)


def test_sentence_window_projection_distinguishes_indexed_text_from_context() -> None:
    result = chunk_source(
        b"First paragraph has a sentence.\n\nSecond paragraph has a sentence.",
        policy=None,
    )

    records = SentenceWindowProjection(result.graph).records()

    assert records[0]["schema_version"] == "catalyst.sentence_window.v1"
    assert "indexed_text" in records[0]
    assert "recovered_context" in records[0]
    assert records[0]["indexed_text"] != records[0]["recovered_context"]


def test_emit_projection_supports_context_views() -> None:
    result = chunk_source(b"# Title\n\nFirst paragraph.\n\nSecond paragraph.")

    parent_child = emit_projection(result, "parent_child")
    sentence_window = emit_projection(result, "sentence_window")

    assert isinstance(parent_child, dict)
    assert parent_child["schema_version"] == "catalyst.parent_child.v1"
    assert isinstance(sentence_window, list)
    assert sentence_window[0]["schema_version"] == "catalyst.sentence_window.v1"
