"""Mappings from derived structures back to source spans."""

from __future__ import annotations

from dataclasses import dataclass, field

from catalyst.source.records.source_span import SourceSpan


@dataclass(frozen=True)
class LineageMap:
    """Immutable derived-id to source-span map."""

    entries: dict[str, tuple[SourceSpan, ...]] = field(default_factory=dict)

    def spans_for(self, derived_id: str) -> tuple[SourceSpan, ...]:
        return self.entries.get(derived_id, ())
