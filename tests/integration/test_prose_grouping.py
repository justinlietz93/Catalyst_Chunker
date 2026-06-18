from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.operation.commands.chunk_source import chunk_source


def test_short_paragraphs_merge_under_target_policy() -> None:
    result = chunk_source(
        b"# Title\n\nSmall one.\n\nSmall two.",
        policy=SelectionPolicy(target_tokens=20, hard_max_tokens=30),
    )

    assert len(result.graph.chunks) == 1
    assert "Small one" in result.graph.chunks[0].text
    assert "Small two" in result.graph.chunks[0].text


def test_structural_evidence_is_attached_to_prose_candidate() -> None:
    result = chunk_source(
        b"# Title\n\n- first\n- second\n\n| A | B |\n|---|---|\n| 1 | 2 |",
        policy=SelectionPolicy(target_tokens=50, hard_max_tokens=60),
    )
    evidence_ids = set(result.graph.chunks[0].evidence_ids)
    evidence_by_id = {obs.observation_id: obs for obs in result.evidence.observations}
    kinds = {evidence_by_id[evidence_id].kind for evidence_id in evidence_ids}

    assert {"markdown_heading", "paragraph", "list_item", "table_row", "sentence", "token_count"} <= kinds
