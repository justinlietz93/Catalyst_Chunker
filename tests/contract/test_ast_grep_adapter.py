import json

from catalyst.boundary.adapters.ast_grep.ast_grep_parser import AstGrepParser
from catalyst.boundary.ports.ast_parser_port import AstParserPort
from catalyst.source.records.source_record import SourceRecord


def test_ast_grep_parser_satisfies_ast_parser_port() -> None:
    parser = AstGrepParser(runner=_fake_ast_grep_runner)
    source = SourceRecord.from_bytes(
        b"import os\n\n"
        b"def helper():\n"
        b"    return os.getcwd()\n",
        source_kind="code",
    )

    parsed = parser.parse(source, "python")

    assert isinstance(parser, AstParserPort)
    assert parsed.language == "python"
    assert parsed.evidence.by_kind("code_import")
    assert parsed.evidence.by_kind("code_function")
    assert parsed.evidence.by_kind("code_block")
    assert parsed.evidence.by_kind("code_call")


def test_ast_grep_parser_uses_utf8_byte_offsets_as_source_spans() -> None:
    source = SourceRecord.from_bytes("x = 'π'\nhelper()\n".encode(), source_kind="code")
    byte_start = len("x = 'π'\n".encode())
    byte_end = byte_start + len("helper()".encode())

    def runner(command: tuple[str, ...], _text: str) -> str:
        pattern = command[command.index("--pattern") + 1]
        if pattern != "$CALL($$$ARGS)":
            return "[]"
        return json.dumps(
            [
                _match(
                    "helper()",
                    byte_start,
                    byte_end,
                    line_start=1,
                    line_end=1,
                    meta_name="CALL",
                    meta_text="helper",
                )
            ]
        )

    parser = AstGrepParser(runner=runner)

    parsed = parser.parse(source, "python")
    call = parsed.evidence.by_kind("code_call")[0]

    assert source.text_for(call.span) == "helper()"


def _fake_ast_grep_runner(command: tuple[str, ...], source_text: str) -> str:
    pattern = command[command.index("--pattern") + 1]
    if pattern == "import $MODULE":
        return json.dumps(
            [_match("import os", 0, len("import os"), meta_name="MODULE", meta_text="os")]
        )
    if pattern == "def $NAME($$$PARAMS): $$$BODY":
        start = source_text.index("def helper")
        return json.dumps(
            [
                _match(
                    source_text[start:],
                    start,
                    len(source_text),
                    line_start=2,
                    line_end=3,
                    meta_name="NAME",
                    meta_text="helper",
                )
            ]
        )
    if pattern == "$CALL($$$ARGS)":
        start = source_text.index("os.getcwd")
        end = start + len("os.getcwd()")
        return json.dumps(
            [
                _match(
                    "os.getcwd()",
                    start,
                    end,
                    line_start=3,
                    line_end=3,
                    meta_name="CALL",
                    meta_text="getcwd",
                )
            ]
        )
    return "[]"


def _match(
    text: str,
    byte_start: int,
    byte_end: int,
    *,
    line_start: int = 0,
    line_end: int = 0,
    meta_name: str,
    meta_text: str,
) -> dict[str, object]:
    return {
        "text": text,
        "range": {
            "byteOffset": {"start": byte_start, "end": byte_end},
            "start": {"line": line_start, "column": 0},
            "end": {"line": line_end, "column": max(byte_end - byte_start, 0)},
        },
        "metaVariables": {
            "single": {
                meta_name: {
                    "text": meta_text,
                    "range": {
                        "byteOffset": {"start": byte_start, "end": byte_end},
                        "start": {"line": line_start, "column": 0},
                        "end": {"line": line_end, "column": max(byte_end - byte_start, 0)},
                    },
                }
            },
            "multi": {},
            "transformed": {},
        },
    }
