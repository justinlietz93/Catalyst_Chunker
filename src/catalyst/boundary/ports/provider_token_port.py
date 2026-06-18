"""Provider-token boundary port."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class ProviderTokenMeasure:
    """Provider tokenizer count for source text."""

    token_count: int
    provider: str
    model_identity: str
    tokenizer_name: str

    def to_dict(self) -> dict[str, object]:
        return {
            "token_count": self.token_count,
            "provider": self.provider,
            "model_identity": self.model_identity,
            "tokenizer_name": self.tokenizer_name,
        }


@runtime_checkable
class ProviderTokenPort(Protocol):
    """Boundary port for downstream model token counters."""

    def measure(self, text: str) -> ProviderTokenMeasure:
        """Return provider-token accounting for text."""
