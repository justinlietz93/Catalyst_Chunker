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


def test_source_measure_observation_records_characters_bytes_and_atomic_runs() -> None:
    source = SourceRecord.from_bytes("alpha βeta\n漢字🙂".encode(), source_kind="text")

    evidence = observe_source(source)
    measure = evidence.by_kind("source_measure")[0]

    assert measure.payload["character_count"] == len(source.canonical_text)
    assert measure.payload["byte_count"] == len(source.canonical_text.encode("utf-8"))
    assert measure.payload["line_count"] == 2
    assert measure.payload["lexical_token_count"] == 3
    assert measure.payload["max_atomic_run_characters"] == len("alpha")


def test_source_measure_exposes_long_atomic_run_without_changing_token_count() -> None:
    source = SourceRecord.from_bytes(b"a" * 5000, source_kind="text")

    evidence = observe_source(source)
    measure = evidence.by_kind("source_measure")[0]
    token_count = evidence.by_kind("token_count")[0]

    assert measure.payload["character_count"] == 5000
    assert measure.payload["max_atomic_run_characters"] == 5000
    assert measure.payload["lexical_token_count"] == 1
    assert token_count.payload["token_count"] == 1
