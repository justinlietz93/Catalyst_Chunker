"""AST parser boundary port."""

from __future__ import annotations

from typing import Protocol


class AstParserPort(Protocol):
    """Boundary port for AST parser adapters."""

    def parse(self, text: str, language: str) -> object:
        """Parse source text for one language."""
