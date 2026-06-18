"""JSON and JSONL artifact writing."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from pathlib import Path


class JsonlArtifactWriter:
    """Write public projection records as JSON or JSONL."""

    def write_records(self, location: str, records: Iterable[Mapping[str, object]]) -> None:
        path = Path(location)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, sort_keys=True))
                handle.write("\n")

    def write_record(self, location: str, record: Mapping[str, object]) -> None:
        path = Path(location)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
