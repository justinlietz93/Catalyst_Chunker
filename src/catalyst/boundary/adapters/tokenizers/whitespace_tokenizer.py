"""Whitespace tokenizer adapter."""

from __future__ import annotations

from catalyst.observation.instruments.tokenizer_instrument import count_tokens


class WhitespaceTokenizer:
    """Boundary adapter for the baseline whitespace tokenizer."""

    def count(self, text: str) -> int:
        return count_tokens(text)
