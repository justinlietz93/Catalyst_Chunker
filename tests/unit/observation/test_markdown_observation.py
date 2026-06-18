from catalyst.observation.instruments.collect import observe_source
from catalyst.source.records.source_record import SourceRecord


def test_markdown_heading_observation_ignores_code_fences() -> None:
    source = SourceRecord.from_bytes(
        b"# Real Heading\n\n```python\n# Not Heading\n```\n\nBody text.",
        source_kind="markdown",
    )

    evidence = observe_source(source)
    headings = evidence.by_kind("markdown_heading")

    assert len(headings) == 1
    assert headings[0].payload["title"] == "Real Heading"


def test_observations_reference_source_without_mutating_it() -> None:
    source = SourceRecord.from_bytes(b"First paragraph.\n\nSecond paragraph.")
    before = source.canonical_text

    evidence = observe_source(source)

    assert source.canonical_text == before
    assert evidence.by_kind("paragraph")
    assert all(obs.span.source_id == source.source_id for obs in evidence.observations)
