from catalyst.observation.instruments.collect import observe_source
from catalyst.source.records.source_record import SourceRecord


def test_list_and_table_observations_are_source_referenced() -> None:
    source = SourceRecord.from_bytes(
        b"- first\n- second\n\n| A | B |\n|---|---|\n| 1 | 2 |",
        source_kind="markdown",
    )

    evidence = observe_source(source)

    assert len(evidence.by_kind("list_item")) == 2
    assert len(evidence.by_kind("table_row")) == 3
    assert all(obs.span.source_id == source.source_id for obs in evidence.observations)
