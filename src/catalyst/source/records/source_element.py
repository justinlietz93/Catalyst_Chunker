"""Source-native element reference."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from catalyst.source.records.source_span import SourceSpan


@dataclass(frozen=True)
class SourceElement:
    """A source-native element observed before chunk formation."""

    element_id: str
    element_kind: str
    span: SourceSpan
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, object]:
        return {
            "element_id": self.element_id,
            "element_kind": self.element_kind,
            "span": self.span.to_dict(),
            "metadata": dict(self.metadata),
        }
