"""Invariant result."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.shared.ids import stable_id


@dataclass(frozen=True)
class InvariantResult:
    """Reportable invariant outcome."""

    invariant_id: str
    passed: bool
    message: str
    evidence_ids: tuple[str, ...] = ()

    @property
    def result_id(self) -> str:
        return stable_id("invres", self.invariant_id, self.passed, self.message, self.evidence_ids)

    def to_dict(self) -> dict[str, object]:
        return {
            "result_id": self.result_id,
            "invariant_id": self.invariant_id,
            "passed": self.passed,
            "message": self.message,
            "evidence_ids": list(self.evidence_ids),
        }
