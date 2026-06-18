from catalyst.observation.instruments.collect import observe_source
from catalyst.source.records.source_record import SourceRecord


def test_fake_heading_inside_code_fence_is_not_heading() -> None:
    source = SourceRecord.from_bytes(
        b"# Real\n\n```python\n# Fake\n```\n\nText.",
        source_kind="markdown",
    )

    headings = observe_source(source).by_kind("markdown_heading")

    assert len(headings) == 1
    assert headings[0].payload["title"] == "Real"


def test_unclosed_code_fence_does_not_create_later_fake_heading() -> None:
    source = SourceRecord.from_bytes(
        b"# Real\n\n```\n# Fake after malformed fence\nstill code",
        source_kind="markdown",
    )

    headings = observe_source(source).by_kind("markdown_heading")

    assert len(headings) == 1
    assert headings[0].payload["title"] == "Real"
