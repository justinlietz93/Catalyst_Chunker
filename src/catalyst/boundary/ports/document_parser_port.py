"""Document parser boundary port."""

from __future__ import annotations

from typing import Protocol


class DocumentParserPort(Protocol):
    """Boundary port for document parser adapters."""

    def parse(self, raw_bytes: bytes) -> object:
        """Parse raw bytes into adapter output."""
