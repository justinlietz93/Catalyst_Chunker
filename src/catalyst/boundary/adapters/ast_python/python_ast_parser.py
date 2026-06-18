"""Python stdlib AST boundary adapter."""

from __future__ import annotations

import ast

from catalyst.boundary.ports.parsed_code import ParsedCode
from catalyst.observation.evidence.evidence_set import EvidenceSet
from catalyst.observation.evidence.observation import Observation
from catalyst.observation.instruments.span_tools import span_from_chars
from catalyst.shared.ids import stable_id
from catalyst.source.records.source_record import SourceRecord
from catalyst.source.records.source_span import SourceSpan


class PythonAstParser:
    """Translate Python AST structure into Catalyst observations."""

    def parse(self, source: SourceRecord, language: str = "py") -> ParsedCode:
        if language not in {"py", "python"}:
            return ParsedCode(
                source=source,
                evidence=EvidenceSet(source.source_id, ()),
                language=language,
                warnings=(f"unsupported language for PythonAstParser: {language}",),
            )
        try:
            tree = ast.parse(source.canonical_text)
        except SyntaxError as exc:
            return ParsedCode(
                source=source,
                evidence=EvidenceSet(source.source_id, (_syntax_error_observation(source, exc),)),
                language="python",
                warnings=("python syntax error observed",),
            )
        observations = tuple(_observations_for_tree(source, tree))
        return ParsedCode(
            source=source,
            evidence=EvidenceSet(source.source_id, observations),
            language="python",
        )


def _observations_for_tree(source: SourceRecord, tree: ast.AST) -> list[Observation]:
    observations: list[Observation] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            observations.append(_node_observation(source, node, "code_function", {"name": node.name}))
            observations.append(_node_observation(source, node, "code_block", {"block_kind": "function"}))
        elif isinstance(node, ast.ClassDef):
            observations.append(_node_observation(source, node, "code_class", {"name": node.name}))
            observations.append(_node_observation(source, node, "code_block", {"block_kind": "class"}))
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            observations.append(_node_observation(source, node, "code_import", {"module": _module_name(node)}))
        elif isinstance(node, ast.Call):
            observations.append(_node_observation(source, node, "code_call", {"call": _call_name(node)}))
    return observations


def _node_observation(source: SourceRecord, node: ast.AST, kind: str, payload: dict[str, object]) -> Observation:
    span = _span_for_node(source, node)
    return Observation(
        observation_id=stable_id("obs", source.source_id, kind, span.start_char, span.end_char, payload),
        kind=kind,
        span=span,
        confidence=1.0,
        weight=1.0,
        instrument="python_ast",
        payload=payload,
    )


def _span_for_node(source: SourceRecord, node: ast.AST) -> SourceSpan:
    line_start = getattr(node, "lineno", 1)
    line_end = getattr(node, "end_lineno", line_start)
    col_start = getattr(node, "col_offset", 0)
    col_end = getattr(node, "end_col_offset", col_start)
    start = _line_col_to_char(source.canonical_text, line_start, col_start)
    end = _line_col_to_char(source.canonical_text, line_end, col_end)
    return span_from_chars(source, start, end, line_start=line_start, line_end=line_end)


def _syntax_error_observation(source: SourceRecord, error: SyntaxError) -> Observation:
    line = error.lineno or 1
    offset = max((error.offset or 1) - 1, 0)
    start = _line_char_offset_to_char(source.canonical_text, line, offset)
    end = min(len(source.canonical_text), max(start + 1, start + len(error.text or "")))
    return Observation(
        observation_id=stable_id("obs", source.source_id, "code_malformed", line, offset),
        kind="code_malformed",
        span=span_from_chars(source, start, end, line_start=line, line_end=line),
        confidence=1.0,
        weight=1.0,
        instrument="python_ast",
        payload={"message": error.msg, "line": line, "offset": offset},
    )


def _line_col_to_char(text: str, line_number: int, col_offset: int) -> int:
    lines = text.splitlines(True)
    if line_number <= 1:
        return _utf8_col_to_char_offset(lines[0] if lines else "", col_offset)
    prefix = sum(len(line) for line in lines[: line_number - 1])
    line = lines[line_number - 1] if line_number - 1 < len(lines) else ""
    return min(prefix + _utf8_col_to_char_offset(line, col_offset), len(text))


def _line_char_offset_to_char(text: str, line_number: int, char_offset: int) -> int:
    lines = text.splitlines(True)
    if line_number <= 1:
        return min(char_offset, len(text))
    prefix = sum(len(line) for line in lines[: line_number - 1])
    line = lines[line_number - 1] if line_number - 1 < len(lines) else ""
    return min(prefix + min(char_offset, len(line)), len(text))


def _utf8_col_to_char_offset(line: str, col_offset: int) -> int:
    remaining = col_offset
    for index, char in enumerate(line):
        char_width = len(char.encode("utf-8"))
        if remaining < char_width:
            return index
        remaining -= char_width
    return len(line)


def _module_name(node: ast.Import | ast.ImportFrom) -> str:
    if isinstance(node, ast.ImportFrom):
        return node.module or ""
    return ",".join(alias.name for alias in node.names)


def _call_name(node: ast.Call) -> str:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return type(func).__name__
