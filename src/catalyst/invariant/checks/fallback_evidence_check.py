"""Fallback evidence invariant."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from catalyst.invariant.rules.invariant_result import InvariantResult


def check_fallback_evidence(candidate_sets: Iterable[Any]) -> InvariantResult:
    """Check that fallback candidate sets cite why fallback was needed."""

    missing: list[str] = []
    for candidate_set in candidate_sets:
        strategy = getattr(candidate_set, "strategy", "")
        if "fallback" not in strategy:
            continue
        reasons = tuple(getattr(candidate_set, "reasons", ()))
        if not reasons or any(not getattr(reason, "evidence_ids", ()) for reason in reasons):
            missing.append(getattr(candidate_set, "candidate_set_id", "<unknown>"))

    if missing:
        return InvariantResult(
            invariant_id="I006",
            passed=False,
            message=f"fallback candidate sets lack fallback evidence: {', '.join(missing)}",
        )
    return InvariantResult(
        invariant_id="I006",
        passed=True,
        message="fallback candidate sets cite fallback evidence when present",
    )
