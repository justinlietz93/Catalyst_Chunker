"""Projection schema invariant."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from catalyst.invariant.rules.invariant_result import InvariantResult


def check_projection_schema(records: Mapping[str, object] | Sequence[Mapping[str, object]]) -> InvariantResult:
    record_list = [records] if isinstance(records, Mapping) else list(records)
    missing = [
        index
        for index, record in enumerate(record_list)
        if not record.get("schema_version") or not record.get("projection_kind")
    ]
    if missing:
        return InvariantResult(
            invariant_id="I010",
            passed=False,
            message=f"projection records missing schema fields at indexes: {missing}",
        )
    return InvariantResult(
        invariant_id="I010",
        passed=True,
        message="all public projection records declare schema_version and projection_kind",
    )
