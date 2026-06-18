"""Offset reversibility invariant."""

from __future__ import annotations

from collections.abc import Iterable

from catalyst.invariant.rules.invariant_result import InvariantResult
from catalyst.source.records.source_record import SourceRecord
from catalyst.source.records.source_span import SourceSpan


def check_offset_reversibility(
    source: SourceRecord,
    spans: Iterable[SourceSpan],
) -> InvariantResult:
    """Check that span byte offsets match canonical UTF-8 text offsets."""

    broken: list[str] = []
    for span in spans:
        if span.source_id != source.source_id:
            broken.append(f"{span.source_id}:{span.start_char}-{span.end_char}:wrong-source")
            continue
        expected_start = len(source.canonical_text[: span.start_char].encode("utf-8"))
        expected_end = len(source.canonical_text[: span.end_char].encode("utf-8"))
        if span.start_byte != expected_start or span.end_byte != expected_end:
            broken.append(f"{span.source_id}:{span.start_char}-{span.end_char}")

    if broken:
        return InvariantResult(
            invariant_id="I003",
            passed=False,
            message=f"source spans have non-reversible offsets: {', '.join(broken)}",
        )
    return InvariantResult(
        invariant_id="I003",
        passed=True,
        message="all source spans preserve reversible offsets",
    )
