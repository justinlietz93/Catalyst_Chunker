"""Invariant definition."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from catalyst.invariant.rules.invariant_result import InvariantResult


@dataclass(frozen=True)
class Invariant:
    """A deterministic rule that must remain true."""

    invariant_id: str
    name: str
    check: Callable[[], InvariantResult]
