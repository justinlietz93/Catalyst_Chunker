"""Invariant violation record."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.invariant.rules.invariant_result import InvariantResult


@dataclass(frozen=True)
class ViolationRecord:
    """A failed invariant retained for audit."""

    result: InvariantResult

    def to_dict(self) -> dict[str, object]:
        return self.result.to_dict()
