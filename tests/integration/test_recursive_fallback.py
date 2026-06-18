from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.operation.commands.chunk_source import chunk_source
from catalyst.operation.commands.emit_projection import emit_projection


def test_recursive_fallback_repairs_oversized_paragraph() -> None:
    text = " ".join(f"word{i}" for i in range(30))

    result = chunk_source(
        text.encode("utf-8"),
        policy=SelectionPolicy(target_tokens=6, hard_max_tokens=8),
    )

    assert result.selection.accepted.strategy == "recursive_fallback"
    assert result.selection.rejections
    assert result.selection.accepted.repairs
    assert all(chunk.token_count <= 8 for chunk in result.graph.chunks)
    assert any(result_id.invariant_id == "I006" for result_id in result.invariant_ledger.results)
    assert all(result_id.passed for result_id in result.invariant_ledger.results)


def test_recursive_fallback_fixed_size_slicing_is_audit_visible() -> None:
    text = " ".join(f"word{i}" for i in range(30))
    result = chunk_source(
        text.encode("utf-8"),
        policy=SelectionPolicy(target_tokens=6, hard_max_tokens=8),
    )

    audit = emit_projection(result, "audit")

    assert isinstance(audit, dict)
    assert audit["fallback_records"][0]["strategy"] == "recursive_fallback"
    assert audit["fallback_records"][0]["fixed_size_slicing_used"] is True
    assert audit["fallback_records"][0]["fixed_size_candidate_ids"]
    assert audit["repairs"][0]["reason"].startswith("fixed-size token windows used")
