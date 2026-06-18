"""Markdown structure observation."""

from __future__ import annotations

import re

from catalyst.observation.evidence.observation import Observation
from catalyst.observation.instruments.span_tools import iter_lines, span_from_chars
from catalyst.shared.ids import stable_id
from catalyst.source.records.source_record import SourceRecord

_HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$")


class MarkdownInstrument:
    """Observe Markdown headings without admitting chunks."""

    name = "markdown"

    def observe(self, source: SourceRecord) -> tuple[Observation, ...]:
        observations: list[Observation] = []
        in_fence = False

        for line_number, start, end, line in iter_lines(source):
            stripped = line.strip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = not in_fence
            if in_fence:
                continue

            match = _HEADING_RE.match(line.rstrip("\r\n"))
            if not match:
                continue

            level = len(match.group(1))
            title = match.group(2).strip()
            span = span_from_chars(
                source,
                start,
                end,
                line_start=line_number,
                line_end=line_number,
            )
            observations.append(
                Observation(
                    observation_id=stable_id("obs", source.source_id, "heading", start, end),
                    kind="markdown_heading",
                    span=span,
                    confidence=1.0,
                    weight=1.0,
                    instrument=self.name,
                    payload={"level": level, "title": title},
                )
            )

        return tuple(observations)
