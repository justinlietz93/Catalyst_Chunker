"""Sentence boundary observation."""

from __future__ import annotations

import re

from catalyst.observation.evidence.observation import Observation
from catalyst.observation.instruments.span_tools import span_from_chars
from catalyst.shared.ids import stable_id
from catalyst.source.records.source_record import SourceRecord

_SENTENCE_RE = re.compile(r"\S(?:.*?)(?:[.!?](?=\s|$)|$)", re.DOTALL)


class SentenceInstrument:
    """Observe sentence-like spans with a lightweight local rule."""

    name = "sentence"

    def observe(self, source: SourceRecord) -> tuple[Observation, ...]:
        observations: list[Observation] = []
        for match in _SENTENCE_RE.finditer(source.canonical_text):
            text = match.group(0)
            if not text.strip():
                continue
            start, end = match.span()
            span = span_from_chars(source, start, end)
            observations.append(
                Observation(
                    observation_id=stable_id("obs", source.source_id, "sentence", start, end),
                    kind="sentence",
                    span=span,
                    confidence=0.75,
                    weight=0.5,
                    instrument=self.name,
                    payload={"text_preview": text.strip()[:80]},
                )
            )
        return tuple(observations)
