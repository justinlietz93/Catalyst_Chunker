from catalyst.source.lineage.offset_map import OffsetMap
from catalyst.source.normalization.reversible_normalizer import ReversibleNormalizer
from catalyst.source.records.source_record import SourceRecord


def test_reversible_normalizer_preserves_text_and_declares_trace() -> None:
    source = SourceRecord.from_bytes(b"alpha\nbeta")

    normalized, trace = ReversibleNormalizer().normalize(source)

    assert normalized.canonical_text == source.canonical_text
    assert normalized.normalization_trace_id == trace.trace_id
    assert trace.reversible
    assert not trace.lossy


def test_offset_map_preserves_identity_offsets() -> None:
    offset_map = OffsetMap(source_id="src")

    assert offset_map.raw_char_for(4) == 4
