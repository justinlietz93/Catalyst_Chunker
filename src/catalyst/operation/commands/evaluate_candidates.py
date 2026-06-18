"""Evaluate candidate sets without hiding rejected structure."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from catalyst.formation.candidates.chunk_candidate_set import ChunkCandidateSet
from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.formation.selection.selector import SelectionResult, select_candidate_set
from catalyst.formation.strategies.paragraph_group_strategy import ParagraphGroupStrategy
from catalyst.formation.strategies.recursive_fallback_strategy import RecursiveFallbackStrategy
from catalyst.formation.strategies.semantic_refinement_strategy import SemanticRefinementStrategy
from catalyst.observation.evidence.evidence_set import EvidenceSet
from catalyst.observation.instruments.collect import observe_source
from catalyst.observation.instruments.semantic_shift_instrument import SemanticShiftInstrument
from catalyst.projection.schemas.schema_version import CANDIDATE_EVALUATION_SCHEMA_VERSION
from catalyst.source.records.source_record import SourceRecord


@dataclass(frozen=True)
class CandidateEvaluation:
    """Inspectable candidate comparison."""

    source: SourceRecord
    evidence: EvidenceSet
    candidate_sets: tuple[ChunkCandidateSet, ...]
    selection: SelectionResult
    policy: SelectionPolicy

    def record(self) -> dict[str, object]:
        hard_gates = {
            candidate_set.candidate_set_id: _hard_gate_result(
                candidate_set,
                self.selection.decision.policy_id,
                self.policy,
            )
            for candidate_set in self.candidate_sets
        }
        soft_metrics = {
            candidate_set.candidate_set_id: _soft_metrics(candidate_set, self.evidence)
            for candidate_set in self.candidate_sets
        }
        return {
            "schema_version": CANDIDATE_EVALUATION_SCHEMA_VERSION,
            "projection_kind": "candidate_evaluation",
            "source_id": self.source.source_id,
            "candidate_sets": [candidate_set.to_dict() for candidate_set in self.candidate_sets],
            "hard_gate_results": hard_gates,
            "soft_metrics": soft_metrics,
            "accepted_candidate_set": self.selection.accepted.candidate_set_id,
            "decision": self.selection.decision.to_dict(),
            "rejections": [rejection.to_dict() for rejection in self.selection.rejections],
            "repairs": [
                repair.to_dict()
                for candidate_set in self.candidate_sets
                for repair in candidate_set.repairs
            ],
            "selected_graph": _selected_graph_preview(self.selection),
        }


def evaluate_candidates(
    raw_bytes: bytes,
    *,
    location: str | None = None,
    policy: SelectionPolicy | None = None,
) -> CandidateEvaluation:
    """Compare candidate sets for one source without emitting chunks."""

    active_policy = policy or SelectionPolicy()
    source = SourceRecord.from_bytes(raw_bytes, source_kind="markdown", location=location)
    evidence = observe_source(source)
    if active_policy.allow_semantic_refinement:
        semantic_observations = SemanticShiftInstrument().observe(source)
        evidence = EvidenceSet(
            source_id=evidence.source_id,
            observations=(*evidence.observations, *semantic_observations),
        )
    paragraph_set = ParagraphGroupStrategy().form(source, evidence, active_policy)
    semantic_set = SemanticRefinementStrategy().form(
        source,
        evidence,
        active_policy,
        structural_candidate_set=paragraph_set,
    )
    recursive_set = RecursiveFallbackStrategy().form(
        source,
        evidence,
        active_policy,
        failed_candidate_set_id=paragraph_set.candidate_set_id,
    )
    candidate_sets = (
        (semantic_set, paragraph_set, recursive_set)
        if semantic_set.candidates
        else (paragraph_set, recursive_set)
    )
    selection = select_candidate_set(candidate_sets, active_policy)
    return CandidateEvaluation(
        source=source,
        evidence=evidence,
        candidate_sets=candidate_sets,
        selection=selection,
        policy=active_policy,
    )


def _hard_gate_result(
    candidate_set: ChunkCandidateSet,
    policy_id: str,
    policy: SelectionPolicy,
) -> dict[str, object]:
    oversized = [
        candidate.candidate_id
        for candidate in candidate_set.candidates
        if candidate.token_count > policy.hard_max_tokens
    ]
    return {
        "policy_id": policy_id,
        "has_candidates": bool(candidate_set.candidates),
        "token_budget": not oversized,
        "oversized_candidate_ids": oversized,
        "passed": bool(candidate_set.candidates) and not oversized,
    }


def _soft_metrics(candidate_set: ChunkCandidateSet, evidence: EvidenceSet) -> dict[str, object]:
    candidates = candidate_set.candidates
    token_total = sum(candidate.token_count for candidate in candidates)
    semantic_ids = _candidate_semantic_evidence_ids(candidate_set, evidence)
    chunk_count = len(candidates)
    repair_count = sum(candidate.metrics.repair_count for candidate in candidates) + len(candidate_set.repairs)
    orphan_count = sum(candidate.metrics.orphan_count for candidate in candidates)
    return {
        "boundary_clarity": _rounded(_boundary_clarity(candidate_set)),
        "chunk_stickiness": _rounded(_chunk_stickiness(candidate_set)),
        "context_coherence": _rounded(_context_coherence(candidate_set)),
        "orphan_count": orphan_count,
        "repair_count": repair_count,
        "semantic_discontinuity": _rounded(_semantic_discontinuity(semantic_ids, evidence)),
        "index_cost_estimate": {
            "chunk_count": chunk_count,
            "token_total": token_total,
        },
        "latency_estimate": {
            "relative_units": chunk_count + repair_count + len(semantic_ids),
        },
    }


def _boundary_clarity(candidate_set: ChunkCandidateSet) -> float:
    if not candidate_set.candidates:
        return 0.0
    cited = sum(1 for candidate in candidate_set.candidates if candidate.evidence_ids)
    return cited / len(candidate_set.candidates)


def _chunk_stickiness(candidate_set: ChunkCandidateSet) -> float:
    if not candidate_set.candidates:
        return 0.0
    weak = sum(
        1
        for candidate in candidate_set.candidates
        if any(_warning_reduces_stickiness(warning) for warning in candidate.warnings)
    )
    return 1.0 - (weak / len(candidate_set.candidates))


def _context_coherence(candidate_set: ChunkCandidateSet) -> float:
    if not candidate_set.candidates:
        return 0.0
    coherent = 0
    for candidate in candidate_set.candidates:
        spans = sorted(candidate.spans, key=lambda span: span.start_char)
        if not spans:
            continue
        if all(left.end_char <= right.start_char for left, right in zip(spans, spans[1:])):
            coherent += 1
    return coherent / len(candidate_set.candidates)


def _candidate_semantic_evidence_ids(
    candidate_set: ChunkCandidateSet,
    evidence: EvidenceSet,
) -> tuple[str, ...]:
    semantic_ids: list[str] = []
    for candidate in candidate_set.candidates:
        for evidence_id in candidate.evidence_ids:
            observation = evidence.by_id(evidence_id)
            if observation is not None and observation.kind == "semantic_shift":
                semantic_ids.append(evidence_id)
    return tuple(dict.fromkeys(semantic_ids))


def _semantic_discontinuity(semantic_ids: tuple[str, ...], evidence: EvidenceSet) -> float:
    values: list[float] = []
    for evidence_id in semantic_ids:
        observation = evidence.by_id(evidence_id)
        if observation is None:
            continue
        value = observation.payload.get("discontinuity")
        if isinstance(value, (float, int)):
            values.append(float(value))
    if not values:
        return 0.0
    return sum(values) / len(values)


def _selected_graph_preview(selection: SelectionResult) -> dict[str, object]:
    return {
        "graph_kind": "candidate_selection_preview",
        "candidate_set_id": selection.accepted.candidate_set_id,
        "chunks": [
            {
                "candidate_id": candidate.candidate_id,
                "source_id": candidate.source_id,
                "token_count": candidate.token_count,
                "source_spans": [span.to_dict() for span in candidate.spans],
                "evidence_ids": list(candidate.evidence_ids),
                "warnings": list(candidate.warnings),
            }
            for candidate in selection.accepted.candidates
        ],
    }


def _rounded(value: Any) -> float:
    return round(float(value), 6)


def _warning_reduces_stickiness(warning: str) -> bool:
    lowered = warning.lower()
    return "exceeds" in lowered or "rejection" in lowered or "repair required" in lowered
