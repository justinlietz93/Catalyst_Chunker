"""Semantic refinement candidate formation."""

from __future__ import annotations

from catalyst.formation.candidates.candidate_metrics import CandidateMetrics
from catalyst.formation.candidates.candidate_reason import CandidateReason
from catalyst.formation.candidates.chunk_candidate import ChunkCandidate
from catalyst.formation.candidates.chunk_candidate_set import ChunkCandidateSet
from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.observation.evidence.evidence_set import EvidenceSet
from catalyst.observation.evidence.observation import Observation
from catalyst.observation.instruments.tokenizer_instrument import count_tokens
from catalyst.shared.ids import stable_id
from catalyst.source.records.source_record import SourceRecord
from catalyst.source.records.source_span import SourceSpan


class SemanticRefinementStrategy:
    """Refine existing structural candidates using semantic shift evidence."""

    strategy = "semantic_refinement"

    def form(
        self,
        source: SourceRecord,
        evidence: EvidenceSet,
        policy: SelectionPolicy,
        *,
        structural_candidate_set: ChunkCandidateSet,
    ) -> ChunkCandidateSet:
        if not policy.allow_semantic_refinement:
            return _empty_set(
                source,
                self.strategy,
                "semantic_refinement_policy_disabled",
                "semantic refinement policy is disabled",
            )
        if not structural_candidate_set.candidates:
            return _empty_set(
                source,
                self.strategy,
                "semantic_refinement_requires_structure",
                "semantic refinement requires existing structural candidates",
            )

        shifts = tuple(evidence.by_kind("semantic_shift"))
        if not shifts:
            return _empty_set(
                source,
                self.strategy,
                "semantic_refinement_requires_shift_evidence",
                "semantic refinement requires semantic shift evidence",
            )

        candidates: list[ChunkCandidate] = []
        reasons: list[CandidateReason] = []
        split_count = 0
        for structural_candidate in structural_candidate_set.candidates:
            groups = _split_candidate_spans(structural_candidate.spans, shifts)
            if len(groups) > 1:
                split_count += len(groups) - 1
            for group in groups:
                candidate, reason = self._candidate_from_group(
                    source=source,
                    evidence=evidence,
                    spans=group,
                    structural_candidate_id=structural_candidate.candidate_id,
                )
                candidates.append(candidate)
                reasons.append(reason)

        if split_count == 0:
            return _empty_set(
                source,
                self.strategy,
                "semantic_refinement_no_boundary_change",
                "semantic evidence did not refine structural boundaries",
                evidence_ids=tuple(obs.observation_id for obs in shifts),
            )

        return ChunkCandidateSet(
            candidate_set_id=stable_id(
                "candset",
                source.source_id,
                self.strategy,
                structural_candidate_set.candidate_set_id,
                tuple(candidate.candidate_id for candidate in candidates),
            ),
            strategy=self.strategy,
            source_id=source.source_id,
            candidates=tuple(candidates),
            reasons=tuple(reasons),
            warnings=("semantic refinement applied after structural grouping",),
        )

    def _candidate_from_group(
        self,
        *,
        source: SourceRecord,
        evidence: EvidenceSet,
        spans: tuple[SourceSpan, ...],
        structural_candidate_id: str,
    ) -> tuple[ChunkCandidate, CandidateReason]:
        text = _join_spans(source, spans)
        structural_evidence_ids = _structural_evidence_ids(evidence, spans)
        semantic_evidence_ids = _semantic_evidence_ids(evidence, spans)
        evidence_ids = tuple(dict.fromkeys((*structural_evidence_ids, *semantic_evidence_ids)))
        reason = CandidateReason(
            reason_id=stable_id("reason", source.source_id, self.strategy, structural_candidate_id, spans),
            kind="semantic_refinement_after_structural_candidate",
            evidence_ids=evidence_ids,
            description="semantic shift evidence refined an existing structural candidate",
        )
        token_count = count_tokens(text)
        candidate = ChunkCandidate(
            candidate_id=stable_id("cand", source.source_id, self.strategy, spans),
            source_id=source.source_id,
            spans=spans,
            text=text,
            token_count=token_count,
            evidence_ids=evidence_ids,
            reason_ids=(reason.reason_id,),
            metrics=CandidateMetrics(
                token_count=token_count,
                boundary_count=max(len(spans) - 1, 0),
            ),
            warnings=("formed by semantic refinement evidence",),
        )
        return candidate, reason


def _empty_set(
    source: SourceRecord,
    strategy: str,
    kind: str,
    description: str,
    *,
    evidence_ids: tuple[str, ...] = (),
) -> ChunkCandidateSet:
    reason = CandidateReason(
        reason_id=stable_id("reason", source.source_id, strategy, kind, evidence_ids),
        kind=kind,
        evidence_ids=evidence_ids,
        description=description,
    )
    return ChunkCandidateSet(
        candidate_set_id=stable_id("candset", source.source_id, strategy, kind, evidence_ids),
        strategy=strategy,
        source_id=source.source_id,
        candidates=(),
        reasons=(reason,),
        warnings=(description,),
    )


def _split_candidate_spans(
    spans: tuple[SourceSpan, ...],
    shifts: tuple[Observation, ...],
) -> tuple[tuple[SourceSpan, ...], ...]:
    if len(spans) <= 1:
        return (spans,)
    groups: list[tuple[SourceSpan, ...]] = []
    current: list[SourceSpan] = []
    for index, span in enumerate(spans):
        current.append(span)
        next_span = spans[index + 1] if index + 1 < len(spans) else None
        if next_span and _has_shift_between(span, next_span, shifts):
            groups.append(tuple(current))
            current = []
    if current:
        groups.append(tuple(current))
    return tuple(groups)


def _has_shift_between(
    left: SourceSpan,
    right: SourceSpan,
    shifts: tuple[Observation, ...],
) -> bool:
    for observation in shifts:
        left_payload = observation.payload.get("left_span")
        right_payload = observation.payload.get("right_span")
        if not isinstance(left_payload, dict) or not isinstance(right_payload, dict):
            continue
        if _span_matches(left, left_payload) and _span_matches(right, right_payload):
            return True
    return False


def _span_matches(span: SourceSpan, payload: dict[object, object]) -> bool:
    return (
        payload.get("source_id") == span.source_id
        and payload.get("start_char") == span.start_char
        and payload.get("end_char") == span.end_char
    )


def _semantic_evidence_ids(evidence: EvidenceSet, spans: tuple[SourceSpan, ...]) -> tuple[str, ...]:
    return tuple(
        observation.observation_id
        for observation in evidence.by_kind("semantic_shift")
        if any(_intersects(span, observation.span) for span in spans)
    )


def _structural_evidence_ids(evidence: EvidenceSet, spans: tuple[SourceSpan, ...]) -> tuple[str, ...]:
    return tuple(
        observation.observation_id
        for observation in evidence.observations
        if observation.kind != "semantic_shift"
        and any(_intersects(span, observation.span) for span in spans)
    )


def _join_spans(source: SourceRecord, spans: tuple[SourceSpan, ...]) -> str:
    start = min(span.start_char for span in spans)
    end = max(span.end_char for span in spans)
    return source.canonical_text[start:end].strip()


def _intersects(left: SourceSpan, right: SourceSpan) -> bool:
    return (
        left.source_id == right.source_id
        and left.start_char < right.end_char
        and right.start_char < left.end_char
    )
