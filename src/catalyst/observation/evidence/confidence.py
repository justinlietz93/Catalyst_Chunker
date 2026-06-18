"""Confidence value object."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Confidence:
    """A bounded confidence score."""

    value: float

    def __post_init__(self) -> None:
        if not 0 <= self.value <= 1:
            raise ValueError("confidence must be between 0 and 1")
