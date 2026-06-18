"""Embedding boundary port."""

from __future__ import annotations

from typing import Protocol


class EmbeddingPort(Protocol):
    """Boundary port for embedding adapters."""

    def embed(self, texts: tuple[str, ...]) -> tuple[tuple[float, ...], ...]:
        """Return embeddings for texts."""
