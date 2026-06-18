"""Offset map placeholder for reversible source transforms."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OffsetMap:
    """Maps canonical character offsets back to raw character offsets."""

    source_id: str

    def raw_char_for(self, canonical_char: int) -> int:
        if canonical_char < 0:
            raise ValueError("offset cannot be negative")
        return canonical_char
