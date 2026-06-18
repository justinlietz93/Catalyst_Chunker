"""Selection decision record."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DecisionRecord:
    """Records why a candidate set was admitted."""

    decision_id: str
    accepted_candidate_set_id: str
    policy_id: str
    reason: str
    evidence_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "decision_id": self.decision_id,
            "accepted_candidate_set_id": self.accepted_candidate_set_id,
            "policy_id": self.policy_id,
            "reason": self.reason,
            "evidence_ids": list(self.evidence_ids),
        }
