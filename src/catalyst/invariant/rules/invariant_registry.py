"""Invariant registry."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.invariant.rules.invariant import Invariant
from catalyst.invariant.rules.invariant_result import InvariantResult


@dataclass(frozen=True)
class InvariantRegistry:
    """Runs invariant checks in a deterministic order."""

    invariants: tuple[Invariant, ...]

    def evaluate(self) -> tuple[InvariantResult, ...]:
        return tuple(invariant.check() for invariant in self.invariants)
