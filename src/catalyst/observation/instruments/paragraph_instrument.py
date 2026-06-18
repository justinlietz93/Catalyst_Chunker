"""Paragraph boundary observation."""

from __future__ import annotations

from catalyst.observation.evidence.observation import Observation
from catalyst.observation.instruments.span_tools import iter_lines, span_from_chars
from catalyst.shared.ids import stable_id
from catalyst.source.records.source_record import SourceRecord


class ParagraphInstrument:
    """Observe contiguous nonblank text regions."""

    name = "paragraph"

    def observe(self, source: SourceRecord) -> tuple[Observation, ...]:
        observations: list[Observation] = []
        para_start: int | None = None
        para_end = 0
        line_start: int | None = None
        line_end: int | None = None

        def emit() -> None:
            if para_start is None or line_start is None or line_end is None:
                return
            text = source.canonical_text[para_start:para_end]
            if not text.strip():
                return
            span = span_from_chars(
                source,
                para_start,
                para_end,
                line_start=line_start,
                line_end=line_end,
            )
            observations.append(
                Observation(
                    observation_id=stable_id("obs", source.source_id, "paragraph", para_start, para_end),
                    kind="paragraph",
                    span=span,
                    confidence=1.0,
                    weight=0.9,
                    instrument=self.name,
                    payload={"text_preview": text.strip()[:80]},
                )
            )

        for line_number, start, end, line in iter_lines(source):
            if line.strip():
                if para_start is None:
                    para_start = start
                    line_start = line_number
                para_end = end
                line_end = line_number
            else:
                emit()
                para_start = None
                line_start = None
                line_end = None

        emit()
        return tuple(observations)
