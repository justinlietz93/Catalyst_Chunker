from types import MappingProxyType

import pytest

from catalyst.source.records.source_record import SourceRecord
from catalyst.source.records.source_span import SourceSpan


def test_source_record_preserves_identity_and_hashes() -> None:
    first = SourceRecord.from_bytes(b"# Title\n\nBody text.", location="doc.md")
    second = SourceRecord.from_bytes(b"# Title\n\nBody text.", location="doc.md")

    assert first.source_id == second.source_id
    assert first.identity.raw_bytes_hash == second.identity.raw_bytes_hash
    assert first.identity.canonical_text_hash == second.identity.canonical_text_hash
    assert first.full_span().source_id == first.source_id


def test_source_record_metadata_is_not_mutable() -> None:
    source = SourceRecord.from_bytes(b"text", metadata={"kind": "fixture"})

    assert isinstance(source.metadata, MappingProxyType)
    with pytest.raises(TypeError):
        source.metadata["kind"] = "changed"  # type: ignore[index]


def test_source_span_rejects_invalid_offsets() -> None:
    with pytest.raises(ValueError):
        SourceSpan(
            source_id="src",
            start_byte=0,
            end_byte=1,
            start_char=4,
            end_char=2,
        )
