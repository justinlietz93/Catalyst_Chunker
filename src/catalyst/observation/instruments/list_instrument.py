"""List structure observation."""

from __future__ import annotations

import re

from catalyst.observation.evidence.observation import Observation
from catalyst.observation.instruments.span_tools import iter_lines, span_from_chars
from catalyst.shared.ids import stable_id
from catalyst.source.records.source_record import SourceRecord

_LIST_RE = re.compile(r"^\s{0,6}([-*+]|\d+(?:\.\d+)*[.)]?|\([A-Za-z0-9]+\)|[A-Za-z][.)])\s+(.+?)\s*$")


class ListInstrument:
    """Observe Markdown-like list items."""

    name = "list"

    def observe(self, source: SourceRecord) -> tuple[Observation, ...]:
        observations: list[Observation] = []
        in_fence = False
        for line_number, start, end, line in iter_lines(source):
            stripped = line.strip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = not in_fence
            if in_fence:
                continue
            match = _LIST_RE.match(line.rstrip("\r\n"))
            if not match:
                continue
            observations.append(
                Observation(
                    observation_id=stable_id("obs", source.source_id, "list_item", start, end),
                    kind="list_item",
                    span=span_from_chars(
                        source,
                        start,
                        end,
                        line_start=line_number,
                        line_end=line_number,
                    ),
                    confidence=0.95,
                    weight=0.8,
                    instrument=self.name,
                    payload={"marker": match.group(1), "text_preview": match.group(2)[:80]},
                )
            )
        return tuple(observations)
