from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.formation.strategies.hierarchical_strategy import HierarchicalStrategy
from catalyst.observation.instruments.collect import observe_source
from catalyst.source.records.source_record import SourceRecord


def test_hierarchical_strategy_forms_parent_and_children() -> None:
    source = SourceRecord.from_bytes(b"# Title\n\nFirst paragraph.\n\nSecond paragraph.")
    evidence = observe_source(source)

    candidate_set = HierarchicalStrategy().form(source, evidence, SelectionPolicy())

    assert candidate_set.strategy == "hierarchical"
    assert candidate_set.candidates[0].spans == (source.full_span(),)
    assert len(candidate_set.candidates) > 1
    assert candidate_set.warnings
