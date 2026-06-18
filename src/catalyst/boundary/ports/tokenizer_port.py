"""Tokenizer boundary port."""

from __future__ import annotations

from typing import Protocol


class TokenizerPort(Protocol):
    """Boundary port for external tokenizer implementations."""

    def count(self, text: str) -> int:
        """Count tokens in text."""
