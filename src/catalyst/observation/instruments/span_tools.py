"""Span helpers for observation instruments."""

from __future__ import annotations

from collections.abc import Iterator

from catalyst.source.records.source_record import SourceRecord
from catalyst.source.records.source_span import SourceSpan


def span_from_chars(
    source: SourceRecord,
    start_char: int,
    end_char: int,
    *,
    line_start: int | None = None,
    line_end: int | None = None,
) -> SourceSpan:
    start_byte = len(source.canonical_text[:start_char].encode("utf-8"))
    end_byte = len(source.canonical_text[:end_char].encode("utf-8"))
    return SourceSpan(
        source_id=source.source_id,
        start_byte=start_byte,
        end_byte=end_byte,
        start_char=start_char,
        end_char=end_char,
        line_start=line_start,
        line_end=line_end,
    )


def iter_lines(source: SourceRecord) -> Iterator[tuple[int, int, int, str]]:
    start = 0
    for line_number, line in enumerate(source.canonical_text.splitlines(True), start=1):
        end = start + len(line)
        yield line_number, start, end, line
        start = end
    if source.canonical_text and not source.canonical_text.endswith(("\n", "\r")):
        return
    if not source.canonical_text:
        return
