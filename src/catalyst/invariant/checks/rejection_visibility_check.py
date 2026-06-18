"""Rejection visibility invariant."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from catalyst.invariant.rules.invariant_result import InvariantResult


def check_rejection_visibility(rejections: Iterable[Any], expected_count: int | None = None) -> InvariantResult:
    rejection_tuple = tuple(rejections)
    if expected_count is not None and len(rejection_tuple) != expected_count:
        return InvariantResult(
            invariant_id="I011",
            passed=False,
            message=f"expected {expected_count} rejection records, found {len(rejection_tuple)}",
        )
    incomplete = [
        getattr(rejection, "rejection_id", "<unknown>")
        for rejection in rejection_tuple
        if not getattr(rejection, "reason", None)
    ]
    if incomplete:
        return InvariantResult(
            invariant_id="I011",
            passed=False,
            message=f"rejection records missing reasons: {', '.join(incomplete)}",
        )
    return InvariantResult(
        invariant_id="I011",
        passed=True,
        message="rejected candidates remain inspectable",
    )
