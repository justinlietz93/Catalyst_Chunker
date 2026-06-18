"""Canonical source record."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from catalyst.shared.ids import content_hash
from catalyst.source.records.source_identity import SourceIdentity
from catalyst.source.records.source_span import SourceSpan


@dataclass(frozen=True)
class SourceRecord:
    """Canonical material received by Catalyst."""

    identity: SourceIdentity
    canonical_text: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
    normalization_trace_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def source_id(self) -> str:
        return self.identity.source_id

    @property
    def source_kind(self) -> str:
        return self.identity.source_kind

    @classmethod
    def from_bytes(
        cls,
        raw_bytes: bytes,
        *,
        source_kind: str = "text",
        location: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> "SourceRecord":
        canonical_text = raw_bytes.decode("utf-8", errors="replace")
        identity = SourceIdentity.from_hashes(
            source_kind=source_kind,
            raw_bytes_hash=content_hash(raw_bytes),
            canonical_text_hash=content_hash(canonical_text),
            location=location,
        )
        return cls(
            identity=identity,
            canonical_text=canonical_text,
            metadata=metadata or {},
        )

    @classmethod
    def from_canonical_text(
        cls,
        raw_bytes: bytes,
        canonical_text: str,
        *,
        source_kind: str,
        location: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> "SourceRecord":
        identity = SourceIdentity.from_hashes(
            source_kind=source_kind,
            raw_bytes_hash=content_hash(raw_bytes),
            canonical_text_hash=content_hash(canonical_text),
            location=location,
        )
        return cls(
            identity=identity,
            canonical_text=canonical_text,
            metadata=metadata or {},
        )

    def full_span(self) -> SourceSpan:
        encoded = self.canonical_text.encode("utf-8")
        return SourceSpan(
            source_id=self.source_id,
            start_byte=0,
            end_byte=len(encoded),
            start_char=0,
            end_char=len(self.canonical_text),
        )

    def text_for(self, span: SourceSpan) -> str:
        if span.source_id != self.source_id:
            raise ValueError("span belongs to a different source")
        return self.canonical_text[span.start_char : span.end_char]

    def to_dict(self) -> dict[str, object]:
        return {
            **self.identity.to_dict(),
            "metadata": dict(self.metadata),
            "normalization_trace_id": self.normalization_trace_id,
        }
