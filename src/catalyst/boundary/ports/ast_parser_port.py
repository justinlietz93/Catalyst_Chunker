"""AST parser boundary port."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from catalyst.boundary.ports.parsed_code import ParsedCode
from catalyst.source.records.source_record import SourceRecord

@runtime_checkable
class AstParserPort(Protocol):
    """Boundary port for AST parser adapters."""

    def parse(self, source: SourceRecord, language: str) -> ParsedCode:
        """Parse source text and return Catalyst-native code evidence."""
