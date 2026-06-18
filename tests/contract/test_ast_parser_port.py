from catalyst.boundary.adapters.ast_python.python_ast_parser import PythonAstParser
from catalyst.boundary.ports.ast_parser_port import AstParserPort
from catalyst.source.records.source_record import SourceRecord


def test_python_ast_parser_satisfies_ast_parser_port() -> None:
    parser = PythonAstParser()
    source = SourceRecord.from_bytes(b"def f():\n    return 1\n", source_kind="code")

    parsed = parser.parse(source, "python")

    assert isinstance(parser, AstParserPort)
    assert parsed.language == "python"
    assert parsed.evidence.by_kind("code_function")


def test_python_ast_parser_reports_malformed_syntax_as_evidence() -> None:
    source = SourceRecord.from_bytes(b"def broken(:\n    pass\n", source_kind="code")

    parsed = PythonAstParser().parse(source, "python")

    assert parsed.evidence.by_kind("code_malformed")
    assert parsed.warnings == ("python syntax error observed",)


def test_python_ast_parser_maps_utf8_byte_columns_to_source_chars() -> None:
    source = SourceRecord.from_bytes(
        "def helper():\n    return 1\n\nx = 'π'; helper()\n".encode(),
        source_kind="code",
    )

    parsed = PythonAstParser().parse(source, "python")
    helper_call = [
        observation
        for observation in parsed.evidence.by_kind("code_call")
        if observation.payload["call"] == "helper"
    ][0]

    assert source.text_for(helper_call.span) == "helper()"
