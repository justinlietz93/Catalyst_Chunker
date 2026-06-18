"""Run record."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RunRecord:
    """A completed operation run."""

    run_id: str
    operation: str
    source_id: str
    graph_id: str | None
    passed: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "operation": self.operation,
            "source_id": self.source_id,
            "graph_id": self.graph_id,
            "passed": self.passed,
        }
