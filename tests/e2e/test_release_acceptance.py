from catalyst.boundary.adapters.ast_python.python_ast_parser import PythonAstParser
from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.operation.commands.chunk_code import chunk_parsed_code
from catalyst.operation.commands.chunk_source import chunk_source
from catalyst.operation.commands.emit_projection import emit_boundary_inspection, emit_projection
from catalyst.projection.views.code_view import CodeProjection
from catalyst.source.records.source_record import SourceRecord
from governance.tools.enforce_boundary_purity import main as boundary_purity_main


def test_markdown_document_admits_retrieval_and_audit_projections() -> None:
    result = chunk_source(b"# Title\n\nBody text for release acceptance.")

    retrieval = emit_projection(result, "retrieval")
    audit = emit_projection(result, "audit")

    assert result.invariant_ledger.passed
    assert retrieval[0]["projection_kind"] == "retrieval"
    assert audit["projection_kind"] == "audit"


def test_default_path_does_not_run_fixed_size_slicing() -> None:
    result = chunk_source(b"# Title\n\nBody text for default chunking.")

    assert "fixed" not in result.selection.accepted.strategy
    assert all("fixed" not in warning.lower() for chunk in result.graph.chunks for warning in chunk.warning_ids)


def test_every_accepted_chunk_has_source_lineage() -> None:
    result = chunk_source(b"# Title\n\nBody text for lineage.")

    assert all(chunk.source_id for chunk in result.graph.chunks)
    assert all(chunk.spans for chunk in result.graph.chunks)


def test_public_projection_records_have_schema_versions() -> None:
    prose = chunk_source(b"# Title\n\nBody text for projections.")
    code_source = SourceRecord.from_bytes(
        b"def helper():\n    return 1\n",
        source_kind="code",
    )
    parsed = PythonAstParser().parse(code_source, "python")
    code = chunk_parsed_code(parsed)
    records = [
        *emit_projection(prose, "retrieval"),
        emit_projection(prose, "audit"),
        emit_projection(prose, "parent_child"),
        *emit_projection(prose, "sentence_window"),
        emit_boundary_inspection(source_id=prose.source.source_id, boundary_candidates=()),
        CodeProjection(code.graph, parsed).record(),
    ]

    assert all(record["schema_version"] for record in records)
    assert all(record["projection_kind"] for record in records)


def test_rejected_candidates_remain_inspectable() -> None:
    text = " ".join(f"word{i}" for i in range(30))
    result = chunk_source(
        text.encode(),
        policy=SelectionPolicy(target_tokens=6, hard_max_tokens=8),
    )

    assert result.selection.rejections
    assert result.selection.rejections[0].to_dict()["reason"]


def test_concrete_boundary_adapters_do_not_import_inward() -> None:
    assert boundary_purity_main() == 0
