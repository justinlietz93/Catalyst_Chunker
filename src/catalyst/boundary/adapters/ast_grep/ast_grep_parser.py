"""ast-grep CLI boundary adapter."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from catalyst.boundary.ports.parsed_code import ParsedCode
from catalyst.observation.evidence.evidence_set import EvidenceSet
from catalyst.observation.evidence.observation import Observation
from catalyst.observation.instruments.span_tools import span_from_chars
from catalyst.shared.errors import CatalystError
from catalyst.shared.ids import stable_id
from catalyst.source.records.source_record import SourceRecord
from catalyst.source.records.source_span import SourceSpan

Runner = Callable[[tuple[str, ...], str], str]


@dataclass(frozen=True)
class _AstGrepQuery:
    kind: str
    pattern: str
    payload_key: str
    meta_name: str
    block_kind: str | None = None


class AstGrepParser:
    """Translate ast-grep JSON matches into Catalyst code observations."""

    def __init__(
        self,
        *,
        executable: str = "ast-grep",
        runner: Runner | None = None,
    ) -> None:
        self._executable = executable
        self._runner = runner or _run_ast_grep

    def parse(self, source: SourceRecord, language: str) -> ParsedCode:
        normalized_language = _normalize_language(language)
        if normalized_language is None:
            return ParsedCode(
                source=source,
                evidence=EvidenceSet(source.source_id, ()),
                language=language,
                warnings=(f"unsupported language for AstGrepParser: {language}",),
            )

        observations: list[Observation] = []
        for query in _queries(normalized_language):
            command = (
                self._executable,
                "run",
                "--pattern",
                query.pattern,
                "--lang",
                normalized_language,
                "--json=compact",
                "--stdin",
            )
            matches = _load_matches(self._runner(command, source.canonical_text))
            observations.extend(_observations_for_matches(source, query, matches))

        return ParsedCode(
            source=source,
            evidence=EvidenceSet(source.source_id, _dedupe(observations)),
            language=normalized_language,
        )


def _run_ast_grep(command: tuple[str, ...], source_text: str) -> str:
    try:
        result = subprocess.run(
            command,
            input=source_text,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except FileNotFoundError as exc:
        raise CatalystError(
            "AstGrepParser requires the ast-grep CLI executable; install ast-grep or use catalyst-chunker[ast-grep]"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise CatalystError("ast-grep parsing timed out") from exc

    if result.returncode != 0:
        message = result.stderr.strip() or "ast-grep command failed"
        raise CatalystError(message)
    return result.stdout


def _load_matches(output: str) -> tuple[dict[str, Any], ...]:
    if not output.strip():
        return ()
    loaded = json.loads(output)
    if isinstance(loaded, list):
        return tuple(item for item in loaded if isinstance(item, dict))
    if isinstance(loaded, dict):
        return (loaded,)
    return ()


def _observations_for_matches(
    source: SourceRecord,
    query: _AstGrepQuery,
    matches: tuple[dict[str, Any], ...],
) -> tuple[Observation, ...]:
    observations: list[Observation] = []
    for item in matches:
        span = _span_from_match(source, item)
        payload = {query.payload_key: _meta_text(item, query.meta_name) or item.get("text", "")}
        observations.append(_observation(source, query.kind, span, payload))
        if query.block_kind:
            observations.append(
                _observation(source, "code_block", span, {"block_kind": query.block_kind})
            )
    return tuple(observations)


def _observation(
    source: SourceRecord,
    kind: str,
    span: SourceSpan,
    payload: dict[str, object],
) -> Observation:
    return Observation(
        observation_id=stable_id("obs", source.source_id, "ast_grep", kind, span.start_char, span.end_char, payload),
        kind=kind,
        span=span,
        confidence=0.95,
        weight=0.95,
        instrument="ast_grep",
        payload=payload,
    )


def _span_from_match(source: SourceRecord, item: dict[str, Any]) -> SourceSpan:
    item_range = item.get("range", {})
    byte_offset = item_range.get("byteOffset", {}) if isinstance(item_range, dict) else {}
    start_byte = int(byte_offset.get("start", 0))
    end_byte = int(byte_offset.get("end", start_byte))
    start_char = _byte_to_char(source.canonical_text, start_byte)
    end_char = _byte_to_char(source.canonical_text, end_byte)
    start_line = _line_number(item_range.get("start")) if isinstance(item_range, dict) else None
    end_line = _line_number(item_range.get("end")) if isinstance(item_range, dict) else None
    return span_from_chars(source, start_char, end_char, line_start=start_line, line_end=end_line)


def _byte_to_char(text: str, byte_offset: int) -> int:
    prefix = text.encode("utf-8")[:byte_offset]
    return len(prefix.decode("utf-8", errors="ignore"))


def _line_number(position: Any) -> int | None:
    if not isinstance(position, dict) or "line" not in position:
        return None
    return int(position["line"]) + 1


def _meta_text(item: dict[str, Any], name: str) -> str | None:
    meta = item.get("metaVariables")
    if not isinstance(meta, dict):
        return None
    single = meta.get("single")
    if not isinstance(single, dict):
        return None
    value = single.get(name)
    if isinstance(value, dict) and value.get("text"):
        return str(value["text"])
    return None


def _dedupe(observations: list[Observation]) -> tuple[Observation, ...]:
    seen: set[tuple[str, int, int, tuple[tuple[str, object], ...]]] = set()
    output: list[Observation] = []
    for observation in sorted(observations, key=lambda obs: (obs.span.start_char, obs.kind)):
        key = (
            observation.kind,
            observation.span.start_char,
            observation.span.end_char,
            tuple(sorted(observation.payload.items())),
        )
        if key in seen:
            continue
        seen.add(key)
        output.append(observation)
    return tuple(output)


def _normalize_language(language: str) -> str | None:
    mapping = {
        "py": "python",
        "python": "python",
        "js": "javascript",
        "javascript": "javascript",
        "ts": "typescript",
        "typescript": "typescript",
        "tsx": "tsx",
        "rust": "rust",
        "rs": "rust",
    }
    return mapping.get(language.lower())


def _queries(language: str) -> tuple[_AstGrepQuery, ...]:
    if language == "python":
        return (
            _AstGrepQuery("code_function", "def $NAME($$$PARAMS): $$$BODY", "name", "NAME", "function"),
            _AstGrepQuery("code_function", "async def $NAME($$$PARAMS): $$$BODY", "name", "NAME", "function"),
            _AstGrepQuery("code_class", "class $NAME: $$$BODY", "name", "NAME", "class"),
            _AstGrepQuery("code_class", "class $NAME($$$BASES): $$$BODY", "name", "NAME", "class"),
            _AstGrepQuery("code_import", "import $MODULE", "module", "MODULE"),
            _AstGrepQuery("code_import", "from $MODULE import $$$NAMES", "module", "MODULE"),
            _AstGrepQuery("code_call", "$CALL($$$ARGS)", "call", "CALL"),
        )
    return ()
