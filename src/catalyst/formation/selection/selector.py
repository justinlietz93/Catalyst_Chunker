"""Candidate set selection."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.formation.candidates.chunk_candidate_set import ChunkCandidateSet
from catalyst.formation.selection.decision_record import DecisionRecord
from catalyst.formation.selection.rejection_record import RejectionRecord
from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.shared.ids import stable_id


@dataclass(frozen=True)
class SelectionResult:
    """Result of selecting an admitted candidate set."""

    accepted: ChunkCandidateSet
    decision: DecisionRecord
    rejections: tuple[RejectionRecord, ...]


def select_candidate_set(
    candidate_sets: tuple[ChunkCandidateSet, ...],
    policy: SelectionPolicy,
) -> SelectionResult:
    """Select the first candidate set that satisfies hard policy gates."""

    rejections: list[RejectionRecord] = []
    for candidate_set in candidate_sets:
        oversized = [
            candidate
            for candidate in candidate_set.candidates
            if candidate.token_count > policy.hard_max_tokens
        ]
        if not candidate_set.candidates:
            rejections.append(
                RejectionRecord(
                    rejection_id=stable_id("rej", candidate_set.candidate_set_id, "empty"),
                    rejected_id=candidate_set.candidate_set_id,
                    reason="candidate set contains no candidates",
                    reconsideration_trigger="source observation produces chunkable spans",
                )
            )
            continue
        if oversized:
            rejections.append(
                RejectionRecord(
                    rejection_id=stable_id("rej", candidate_set.candidate_set_id, "token-budget"),
                    rejected_id=candidate_set.candidate_set_id,
                    reason="candidate set violates hard token budget",
                    source_spans=tuple(span for item in oversized for span in item.spans),
                    reconsideration_trigger="repair or source-family strategy reduces oversized chunks",
                )
            )
            continue

        policy_id = stable_id("policy", policy.to_dict())
        decision = DecisionRecord(
            decision_id=stable_id("decision", candidate_set.candidate_set_id, policy_id),
            accepted_candidate_set_id=candidate_set.candidate_set_id,
            policy_id=policy_id,
            reason="first candidate set satisfying hard policy gates",
            evidence_ids=tuple(
                evidence_id
                for candidate in candidate_set.candidates
                for evidence_id in candidate.evidence_ids
            ),
        )
        return SelectionResult(
            accepted=candidate_set,
            decision=decision,
            rejections=tuple(rejections),
        )

    raise ValueError("no candidate set satisfies selection policy")
