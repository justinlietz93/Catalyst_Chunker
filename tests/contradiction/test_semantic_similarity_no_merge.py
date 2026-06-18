from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.operation.commands.chunk_source import chunk_source


def test_semantic_similarity_does_not_merge_source_distinct_structural_chunks() -> None:
    result = chunk_source(
        b"Shared definition alpha beta.\n\n"
        b"Shared definition alpha gamma.\n",
        policy=SelectionPolicy(
            target_tokens=4,
            hard_max_tokens=20,
            allow_semantic_refinement=True,
        ),
    )

    assert result.selection.accepted.strategy == "paragraph_group"
    assert len(result.graph.chunks) == 2
    assert not result.evidence.by_kind("semantic_shift")
