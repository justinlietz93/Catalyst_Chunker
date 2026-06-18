from catalyst.boundary.adapters.ast_python.python_ast_parser import PythonAstParser
from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.formation.selection.selector import SelectionFailure
from catalyst.operation.commands.chunk_code import chunk_parsed_code
from catalyst.projection.views.code_view import CodeProjection
from catalyst.source.records.source_record import SourceRecord


def test_chunk_parsed_code_admits_code_graph_with_relations() -> None:
    source = SourceRecord.from_bytes(
        b"import os\n\n"
        b"def helper():\n"
        b"    return os.getcwd()\n\n"
        b"def caller():\n"
        b"    return helper()\n",
        source_kind="code",
    )
    parsed = PythonAstParser().parse(source, "python")

    result = chunk_parsed_code(parsed)
    projection = CodeProjection(result.graph, parsed).record()

    assert result.invariant_ledger.passed
    assert all(chunk.chunk_kind == "code" for chunk in result.graph.chunks)
    assert {relation.relation_kind for relation in result.graph.relations} >= {
        "defines",
        "code_calls",
        "previous_sibling",
        "next_sibling",
    }
    assert projection["schema_version"] == "catalyst.code.v1"
    assert projection["chunks"][0]["definitions"]


def test_code_projection_exposes_imports_calls_and_definitions() -> None:
    source = SourceRecord.from_bytes(
        b"import os\n\n"
        b"def helper():\n"
        b"    return os.getcwd()\n",
        source_kind="code",
    )
    parsed = PythonAstParser().parse(source, "python")
    result = chunk_parsed_code(parsed)

    record = CodeProjection(result.graph, parsed).record()
    first = record["chunks"][0]

    assert first["definitions"] == ["helper"]
    assert "os" in first["imports"]
    assert "getcwd" in first["calls"]


def test_malformed_code_admission_exposes_rejection_records() -> None:
    source = SourceRecord.from_bytes(b"def broken(:\n    pass\n", source_kind="code")
    parsed = PythonAstParser().parse(source, "python")

    try:
        chunk_parsed_code(parsed)
    except SelectionFailure as error:
        assert len(error.rejections) == 1
        assert error.rejections[0].reason == "candidate set contains no candidates"
        assert error.rejections[0].evidence_ids == (
            parsed.evidence.by_kind("code_malformed")[0].observation_id,
        )
    else:
        raise AssertionError("malformed code should not admit a code chunk graph")


def test_oversized_code_unit_repairs_with_ast_child_boundaries() -> None:
    source = SourceRecord.from_bytes(
        b"class Big:\n"
        b"    def a(self):\n"
        b"        return one\n"
        b"    def b(self):\n"
        b"        return two\n",
        source_kind="code",
    )
    parsed = PythonAstParser().parse(source, "python")

    result = chunk_parsed_code(parsed, policy=SelectionPolicy(hard_max_tokens=6))
    record = CodeProjection(result.graph, parsed).record()

    assert result.invariant_ledger.passed
    assert result.selection.accepted.repairs
    assert [chunk["definitions"] for chunk in record["chunks"]] == [["Big"], ["a"], ["b"]]
    assert all(chunk.token_count <= 6 for chunk in result.graph.chunks)


def test_unrepairable_oversized_code_unit_exposes_rejection_record() -> None:
    expression = " + ".join(f"word{i}" for i in range(12))
    source = SourceRecord.from_bytes(f"def huge():\n    return {expression}\n".encode(), source_kind="code")
    parsed = PythonAstParser().parse(source, "python")

    try:
        chunk_parsed_code(parsed, policy=SelectionPolicy(hard_max_tokens=6))
    except SelectionFailure as error:
        assert len(error.rejections) == 1
        assert error.rejections[0].reason == "candidate set violates hard token budget"
        assert error.rejections[0].source_spans
        assert error.rejections[0].evidence_ids
    else:
        raise AssertionError("unrepairable oversized code should not admit a graph")
