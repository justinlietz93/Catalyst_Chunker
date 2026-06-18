from catalyst.formation.candidates.chunk_candidate_set import ChunkCandidateSet
from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.formation.selection.selector import SelectionFailure, select_candidate_set
from catalyst.operation.commands import chunk_source
from catalyst.shared.errors import EmptySourceError


def test_empty_source_error_has_structured_record() -> None:
    try:
        chunk_source(b"\n\n", location="empty.md")
    except EmptySourceError as error:
        record = error.to_dict()
    else:
        raise AssertionError("empty source should fail")

    assert record["code"] == "source.empty"
    assert record["message"] == "source contains no chunkable text: empty.md"
    assert record["details"]["location"] == "empty.md"
    assert record["details"]["character_count"] == 2


def test_selection_failure_has_structured_rejection_records() -> None:
    empty = ChunkCandidateSet(
        candidate_set_id="empty_set",
        strategy="fixture",
        source_id="src",
        candidates=(),
        reasons=(),
    )

    try:
        select_candidate_set((empty,), SelectionPolicy())
    except SelectionFailure as error:
        record = error.to_dict()
    else:
        raise AssertionError("empty candidate set should fail")

    assert record["code"] == "selection.failure"
    assert record["details"]["rejection_count"] == 1
    assert record["details"]["rejections"][0]["reason"] == "candidate set contains no candidates"
