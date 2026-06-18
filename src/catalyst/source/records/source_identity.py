"""Stable source identity."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.shared.ids import stable_id


@dataclass(frozen=True)
class SourceIdentity:
    """Identity for material before any chunking claim is made."""

    source_id: str
    source_kind: str
    raw_bytes_hash: str
    canonical_text_hash: str
    location: str | None = None

    @classmethod
    def from_hashes(
        cls,
        *,
        source_kind: str,
        raw_bytes_hash: str,
        canonical_text_hash: str,
        location: str | None = None,
    ) -> "SourceIdentity":
        source_id = stable_id("src", source_kind, raw_bytes_hash)
        return cls(
            source_id=source_id,
            source_kind=source_kind,
            raw_bytes_hash=raw_bytes_hash,
            canonical_text_hash=canonical_text_hash,
            location=location,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "source_kind": self.source_kind,
            "raw_bytes_hash": self.raw_bytes_hash,
            "canonical_text_hash": self.canonical_text_hash,
            "location": self.location,
        }
