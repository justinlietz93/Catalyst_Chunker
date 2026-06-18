"""Normalization policy."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NormalizationPolicy:
    """Declares whether normalization may lose source information."""

    lossy_mode: bool = False
    preserve_offsets: bool = True
