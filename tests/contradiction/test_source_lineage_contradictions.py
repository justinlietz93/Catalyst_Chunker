from catalyst.invariant.checks.offset_reversibility_check import check_offset_reversibility
from catalyst.invariant.checks.source_coverage_check import check_source_coverage
from catalyst.projection.chunks.accepted_chunk import AcceptedChunk
from catalyst.source.records.source_record import SourceRecord
from catalyst.source.records.source_span import SourceSpan


def test_broken_byte_offsets_fail_reversibility() -> None:
    source = SourceRecord.from_bytes("alpha βeta".encode("utf-8"))
    bad_span = SourceSpan(
        source_id=source.source_id,
        start_byte=0,
        end_byte=6,
        start_char=0,
        end_char=len(source.canonical_text),
    )

    result = check_offset_reversibility(source, (bad_span,))

    assert not result.passed
    assert result.invariant_id == "I003"


def test_missing_required_span_fails_coverage() -> None:
    required = SourceSpan(
        source_id="src",
        start_byte=0,
        end_byte=10,
        start_char=0,
        end_char=10,
    )
    covered = SourceSpan(
        source_id="src",
        start_byte=0,
        end_byte=4,
        start_char=0,
        end_char=4,
    )
    chunk = AcceptedChunk(
        chunk_id="chk",
        source_id="src",
        spans=(covered,),
        text="part",
        token_count=1,
        chunk_kind="prose",
        candidate_set_id="set",
        evidence_ids=("obs",),
    )

    result = check_source_coverage(required_spans=(required,), chunks=(chunk,))

    assert not result.passed
    assert result.invariant_id == "I001"


def test_union_coverage_can_satisfy_required_span() -> None:
    required = SourceSpan(
        source_id="src",
        start_byte=0,
        end_byte=10,
        start_char=0,
        end_char=10,
    )
    first = SourceSpan(
        source_id="src",
        start_byte=0,
        end_byte=4,
        start_char=0,
        end_char=4,
    )
    second = SourceSpan(
        source_id="src",
        start_byte=4,
        end_byte=10,
        start_char=4,
        end_char=10,
    )
    chunks = (
        AcceptedChunk("a", "src", (first,), "a", 1, "prose", "set", ("obs",)),
        AcceptedChunk("b", "src", (second,), "b", 1, "prose", "set", ("obs",)),
    )

    result = check_source_coverage(required_spans=(required,), chunks=chunks)

    assert result.passed
