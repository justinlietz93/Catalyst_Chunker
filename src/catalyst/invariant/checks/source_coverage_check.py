"""Source coverage invariant."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from catalyst.invariant.rules.invariant_result import InvariantResult
from catalyst.source.records.source_span import SourceSpan


def check_source_coverage(
    *,
    required_spans: Iterable[SourceSpan],
    chunks: Iterable[Any],
) -> InvariantResult:
    """Check that required source spans are covered by accepted chunks."""

    chunk_spans = tuple(span for chunk in chunks for span in getattr(chunk, "spans", ()))
    missing = [span for span in required_spans if not _covered_by_union(span, chunk_spans)]
    if missing:
        ranges = ", ".join(f"{span.source_id}:{span.start_char}-{span.end_char}" for span in missing)
        return InvariantResult(
            invariant_id="I001",
            passed=False,
            message=f"required source spans are not covered: {ranges}",
        )
    return InvariantResult(
        invariant_id="I001",
        passed=True,
        message="all required source spans are covered by accepted chunks",
    )


def _covered_by_union(required: SourceSpan, candidates: tuple[SourceSpan, ...]) -> bool:
    relevant = sorted(
        (
            span
            for span in candidates
            if span.source_id == required.source_id
            and span.end_char > required.start_char
            and span.start_char < required.end_char
        ),
        key=lambda span: span.start_char,
    )
    cursor = required.start_char
    for span in relevant:
        if span.start_char > cursor:
            return False
        cursor = max(cursor, span.end_char)
        if cursor >= required.end_char:
            return True
    return cursor >= required.end_char
