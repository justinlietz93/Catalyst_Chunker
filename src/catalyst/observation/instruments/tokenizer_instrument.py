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
    """Observe token count without owning chunk boundaries."""

    name = "tokenizer"

    def observe(self, source: SourceRecord) -> tuple[Observation, ...]:
        span = source.full_span()
        token_count = count_tokens(source.canonical_text)
        return (
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
