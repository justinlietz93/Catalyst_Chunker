"""Table structure observation."""

from __future__ import annotations

from catalyst.observation.evidence.observation import Observation
from catalyst.observation.instruments.span_tools import iter_lines, span_from_chars
from catalyst.shared.ids import stable_id
from catalyst.source.records.source_record import SourceRecord


class TableInstrument:
    """Observe simple Markdown table rows."""

    name = "table"

    def observe(self, source: SourceRecord) -> tuple[Observation, ...]:
        observations: list[Observation] = []
        in_fence = False
        lines = list(iter_lines(source))
        for index, (line_number, start, end, line) in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = not in_fence
            if in_fence or "|" not in line:
                continue
            cell_count = max(line.count("|") - 1, 0)
            row_role = _row_role(stripped, lines[index + 1][3].strip() if index + 1 < len(lines) else "")
            observations.append(
                Observation(
                    observation_id=stable_id("obs", source.source_id, "table_row", start, end),
                    kind="table_row",
                    span=span_from_chars(
                        source,
                        start,
                        end,
                        line_start=line_number,
                        line_end=line_number,
                    ),
                    confidence=0.8,
                    weight=0.8,
                    instrument=self.name,
                    payload={
                        "cell_count": cell_count,
                        "row_role": row_role,
                        "text_preview": stripped[:80],
                    },
                )
            )
        return tuple(observations)


def _row_role(stripped: str, next_stripped: str) -> str:
    cells = [cell.strip() for cell in stripped.strip("|").split("|")]
    if cells and all(cell and set(cell) <= {"-", ":"} for cell in cells):
        return "separator"
    next_cells = [cell.strip() for cell in next_stripped.strip("|").split("|")]
    if next_cells and all(cell and set(cell) <= {"-", ":"} for cell in next_cells):
        return "header"
    return "body"
