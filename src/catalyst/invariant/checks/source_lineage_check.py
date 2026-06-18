"""Source lineage invariant."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from catalyst.invariant.rules.invariant_result import InvariantResult


def check_source_lineage(chunks: Iterable[Any]) -> InvariantResult:
    missing: list[str] = []
    for chunk in chunks:
        chunk_id = getattr(chunk, "chunk_id", "<unknown>")
        source_id = getattr(chunk, "source_id", None)
        spans = getattr(chunk, "spans", ())
        if not source_id or not spans:
            missing.append(chunk_id)

    if missing:
        return InvariantResult(
            invariant_id="I002",
            passed=False,
            message=f"chunks missing source lineage: {', '.join(missing)}",
        )
    return InvariantResult(
        invariant_id="I002",
        passed=True,
        message="every accepted chunk preserves source lineage",
    )
