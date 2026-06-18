"""Invariant ledger."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.invariant.rules.invariant_result import InvariantResult


@dataclass(frozen=True)
class InvariantLedger:
    """Stores invariant outcomes for a run."""

    results: tuple[InvariantResult, ...]

    @property
    def passed(self) -> bool:
        return all(result.passed for result in self.results)

    def violations(self) -> tuple[InvariantResult, ...]:
        return tuple(result for result in self.results if not result.passed)

    def to_dict(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "results": [result.to_dict() for result in self.results],
        }
