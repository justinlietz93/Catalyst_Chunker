"""Token budget invariant."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from catalyst.invariant.rules.invariant_result import InvariantResult


def check_token_budget(items: Iterable[Any], hard_max_tokens: int) -> InvariantResult:
    oversized: list[str] = []
    for item in items:
        token_count = getattr(item, "token_count", 0)
        item_id = getattr(item, "chunk_id", getattr(item, "candidate_id", "<unknown>"))
        if token_count > hard_max_tokens:
            oversized.append(f"{item_id}:{token_count}")

    if oversized:
        return InvariantResult(
            invariant_id="I007",
            passed=False,
            message=f"items exceed hard token budget {hard_max_tokens}: {', '.join(oversized)}",
        )
    return InvariantResult(
        invariant_id="I007",
        passed=True,
        message=f"all items satisfy hard token budget {hard_max_tokens}",
    )
