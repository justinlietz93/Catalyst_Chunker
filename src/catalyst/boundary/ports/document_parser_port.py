"""Document parser boundary port."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from catalyst.boundary.ports.parsed_document import ParsedDocument

@runtime_checkable
class DocumentParserPort(Protocol):
    """Boundary port for document parser adapters."""

    def parse(self, raw_bytes: bytes, *, location: str | None = None) -> ParsedDocument:
        """Parse bytes and translate output into Catalyst-native records."""
