from catalyst.boundary.adapters.ast_python.python_ast_parser import PythonAstParser
from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.formation.strategies.ast_code_strategy import AstCodeStrategy
from catalyst.source.records.source_record import SourceRecord


def test_nested_functions_are_evidence_but_not_duplicate_top_level_chunks() -> None:
    source = SourceRecord.from_bytes(
        b"def outer():\n"
        b"    def inner():\n"
        b"        return 1\n"
        b"    return inner()\n",
        source_kind="code",
    )
    parsed = PythonAstParser().parse(source, "python")

    candidate_set = AstCodeStrategy().form(source, parsed.evidence, SelectionPolicy())

    assert len(parsed.evidence.by_kind("code_function")) == 2
    assert len(candidate_set.candidates) == 1
    assert "inner" in candidate_set.candidates[0].text


def test_heading_like_comment_in_code_is_not_markdown_structure() -> None:
    source = SourceRecord.from_bytes(
        b"# Looks Like Heading\n"
        b"def actual():\n"
        b"    return '# also not heading'\n",
        source_kind="code",
    )
    parsed = PythonAstParser().parse(source, "python")

    assert parsed.evidence.by_kind("code_function")
    assert not parsed.evidence.by_kind("markdown_heading")
