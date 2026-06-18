from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.operation.commands.chunk_source import chunk_source


def test_baseline_chunking_runs_without_semantic_refinement_or_embeddings() -> None:
    result = chunk_source(
        b"Alpha beta gamma define the first topic.\n\n"
        b"Zinc copper nickel describe another domain.\n",
        policy=SelectionPolicy(target_tokens=100, hard_max_tokens=100),
    )

    assert result.selection.accepted.strategy == "paragraph_group"
    assert not result.evidence.by_kind("semantic_shift")
    assert len(result.graph.chunks) == 1


def test_policy_enabled_semantic_refinement_can_split_structural_group() -> None:
    result = chunk_source(
        b"Alpha beta gamma define the first topic.\n\n"
        b"Zinc copper nickel describe another domain.\n",
        policy=SelectionPolicy(
            target_tokens=100,
            hard_max_tokens=100,
            allow_semantic_refinement=True,
        ),
    )

    assert result.selection.accepted.strategy == "semantic_refinement"
    assert result.evidence.by_kind("semantic_shift")
    assert len(result.graph.chunks) == 2
    assert all(chunk.warning_ids == ("formed by semantic refinement evidence",) for chunk in result.graph.chunks)
    assert result.invariant_ledger.passed
