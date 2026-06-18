from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.observation.instruments.collect import observe_source
from catalyst.operation.commands.chunk_source import chunk_source
from catalyst.source.records.source_record import SourceRecord


def test_legal_clause_nested_numbering_is_observed_without_flattening_text() -> None:
    raw = (
        b"1. Definitions\n"
        b"1.1 Covered Material means source text.\n"
        b"1.1.1 This subclause limits the definition.\n"
        b"(a) This lettered clause remains attached.\n"
    )
    source = SourceRecord.from_bytes(raw, source_kind="markdown")
    evidence = observe_source(source)
    markers = [item.payload["marker"] for item in evidence.by_kind("list_item")]

    result = chunk_source(raw, policy=SelectionPolicy(target_tokens=60, hard_max_tokens=80))

    assert {"1.", "1.1", "1.1.1", "(a)"} <= set(markers)
    assert "1.1.1 This subclause" in result.graph.chunks[0].text
    assert result.invariant_ledger.passed


def test_transcript_missing_speaker_label_stays_with_local_turn() -> None:
    raw = (
        b"Alice: The source boundary starts here.\n"
        b"This unlabeled continuation belongs to Alice.\n\n"
        b"Bob: The next turn starts after the blank.\n"
    )

    result = chunk_source(raw, policy=SelectionPolicy(target_tokens=12, hard_max_tokens=80))

    assert len(result.graph.chunks) == 2
    assert "Alice:" in result.graph.chunks[0].text
    assert "unlabeled continuation" in result.graph.chunks[0].text
    assert "Bob:" in result.graph.chunks[1].text


def test_scientific_citation_heavy_paragraph_preserves_citation_context() -> None:
    raw = (
        b"Prior work [12, 13] defines the baseline. "
        b"The follow-up result (Smith et al., 2024) narrows the claim.\n\n"
        b"Unrelated implementation notes follow later.\n"
    )

    result = chunk_source(raw, policy=SelectionPolicy(target_tokens=40, hard_max_tokens=80))

    assert "[12, 13]" in result.graph.chunks[0].text
    assert "Smith et al., 2024" in result.graph.chunks[0].text
    assert result.invariant_ledger.passed


def test_definition_dependency_this_means_stays_near_referent() -> None:
    raw = (
        b"A catalyst boundary is the admitted source edge. "
        b"This means later projection text must point back to that edge.\n\n"
        b"Another paragraph can discuss unrelated packaging.\n"
    )

    result = chunk_source(raw, policy=SelectionPolicy(target_tokens=30, hard_max_tokens=80))

    assert "catalyst boundary" in result.graph.chunks[0].text
    assert "This means" in result.graph.chunks[0].text
    assert result.invariant_ledger.passed
