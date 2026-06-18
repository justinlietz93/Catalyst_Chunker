"""Observation evidence."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from catalyst.source.records.source_span import SourceSpan


@dataclass(frozen=True)
class Observation:
    """Something seen in source material before chunk admission."""

    observation_id: str
    kind: str
    span: SourceSpan
    confidence: float
    weight: float
    instrument: str
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        if self.weight < 0:
            raise ValueError("weight cannot be negative")
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))

    def to_dict(self) -> dict[str, object]:
        return {
            "observation_id": self.observation_id,
            "kind": self.kind,
            "span": self.span.to_dict(),
            "confidence": self.confidence,
            "weight": self.weight,
            "instrument": self.instrument,
            "payload": dict(self.payload),
        }
