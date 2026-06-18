from catalyst.formation.selection.rejection_record import RejectionRecord
from catalyst.invariant.checks.offset_reversibility_check import check_offset_reversibility
from catalyst.invariant.checks.projection_schema_check import check_projection_schema
from catalyst.invariant.checks.rejection_visibility_check import check_rejection_visibility
from catalyst.invariant.checks.source_coverage_check import check_source_coverage
from catalyst.invariant.checks.source_lineage_check import check_source_lineage
from catalyst.invariant.checks.token_budget_check import check_token_budget
from catalyst.projection.chunks.accepted_chunk import AcceptedChunk
from catalyst.source.records.source_record import SourceRecord
from catalyst.source.records.source_span import SourceSpan


def test_source_coverage_detects_missing_span() -> None:
    source = SourceRecord.from_bytes(b"alpha beta", source_kind="text")
    chunk = _chunk(source, source.full_span())
    missing = SourceSpan(source.source_id, 0, 5, 0, 5)

    assert check_source_coverage(required_spans=(missing,), chunks=(chunk,)).passed
    assert not check_source_coverage(required_spans=(source.full_span(),), chunks=()).passed


def test_source_lineage_detects_missing_spans() -> None:
    source = SourceRecord.from_bytes(b"alpha", source_kind="text")
    valid = _chunk(source, source.full_span())
    invalid = object()

    assert check_source_lineage((valid,)).passed
    assert not check_source_lineage((invalid,)).passed


def test_offset_reversibility_detects_bad_byte_offsets() -> None:
    source = SourceRecord.from_bytes("π alpha".encode(), source_kind="text")
    good = source.full_span()
    bad = SourceSpan(source.source_id, 0, 1, 0, 1)

    assert check_offset_reversibility(source, (good,)).passed
    assert not check_offset_reversibility(source, (bad,)).passed


def test_token_budget_detects_oversized_items() -> None:
    source = SourceRecord.from_bytes(b"alpha beta gamma", source_kind="text")
    chunk = _chunk(source, source.full_span(), token_count=3)

    assert check_token_budget((chunk,), 3).passed
    assert not check_token_budget((chunk,), 2).passed


def test_projection_schema_detects_unversioned_records() -> None:
    assert check_projection_schema({"schema_version": "v", "projection_kind": "x"}).passed
    assert not check_projection_schema({"projection_kind": "x"}).passed


def test_rejection_visibility_counts_expected_records() -> None:
    rejection = RejectionRecord("rej", "candidate", "rejected")

    assert check_rejection_visibility((rejection,), expected_count=1).passed
    assert not check_rejection_visibility((), expected_count=1).passed


def _chunk(
    source: SourceRecord,
    span: SourceSpan,
    *,
    token_count: int = 1,
) -> AcceptedChunk:
    return AcceptedChunk(
        chunk_id="chunk",
        source_id=source.source_id,
        spans=(span,),
        text=source.text_for(span),
        token_count=token_count,
        chunk_kind="fixture",
        candidate_set_id="candidate_set",
        evidence_ids=(),
    )
