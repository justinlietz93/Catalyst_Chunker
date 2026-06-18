"""Tokenizer observation."""

from __future__ import annotations

import re

from catalyst.observation.evidence.observation import Observation
from catalyst.shared.ids import stable_id
from catalyst.source.records.source_record import SourceRecord

_TOKEN_RE = re.compile(r"\S+")


def count_tokens(text: str) -> int:
    """Count whitespace-delimited tokens for the baseline local path."""

    return len(_TOKEN_RE.findall(text))


class TokenizerInstrument:
    """Observe token and source size measures without owning chunk boundaries."""

    name = "tokenizer"

    def observe(self, source: SourceRecord) -> tuple[Observation, ...]:
        span = source.full_span()
        token_count = count_tokens(source.canonical_text)
        encoded = source.canonical_text.encode("utf-8")
        atomic_runs = _TOKEN_RE.findall(source.canonical_text)
        return (
            Observation(
                observation_id=stable_id(
                    "obs",
                    source.source_id,
                    "source_measure",
                    len(source.canonical_text),
                    len(encoded),
                    token_count,
                ),
                kind="source_measure",
                span=span,
                confidence=1.0,
                weight=0.6,
                instrument=self.name,
                payload={
                    "character_count": len(source.canonical_text),
                    "byte_count": len(encoded),
                    "line_count": _line_count(source.canonical_text),
                    "lexical_token_count": token_count,
                    "max_atomic_run_characters": max((len(item) for item in atomic_runs), default=0),
                    "tokenizer": "whitespace",
                },
            ),
            Observation(
                observation_id=stable_id("obs", source.source_id, "token_count", token_count),
                kind="token_count",
                span=span,
                confidence=1.0,
                weight=0.7,
                instrument=self.name,
                payload={"token_count": token_count, "tokenizer": "whitespace"},
            ),
        )


def _line_count(text: str) -> int:
    if not text:
        return 0
    return text.count("\n") + (0 if text.endswith("\n") else 1)
