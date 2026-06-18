"""AST-aware code candidate formation."""

from __future__ import annotations

from catalyst.formation.candidates.candidate_metrics import CandidateMetrics
from catalyst.formation.candidates.candidate_reason import CandidateReason
from catalyst.formation.candidates.chunk_candidate import ChunkCandidate
from catalyst.formation.candidates.chunk_candidate_set import ChunkCandidateSet
from catalyst.formation.repair.repair_record import RepairRecord
from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.observation.evidence.evidence_set import EvidenceSet
from catalyst.observation.evidence.observation import Observation
from catalyst.observation.instruments.span_tools import span_from_chars
from catalyst.observation.instruments.tokenizer_instrument import count_tokens
from catalyst.shared.ids import stable_id
from catalyst.source.records.source_record import SourceRecord
from catalyst.source.records.source_span import SourceSpan


class AstCodeStrategy:
    """Form code chunks from AST-backed observations."""

    strategy = "ast_code"

    def form(
        self,
        source: SourceRecord,
        evidence: EvidenceSet,
        policy: SelectionPolicy,
    ) -> ChunkCandidateSet:
        malformed = evidence.by_kind("code_malformed")
        if malformed:
            return ChunkCandidateSet(
                candidate_set_id=stable_id("candset", source.source_id, self.strategy, "malformed"),
                strategy=self.strategy,
                source_id=source.source_id,
                candidates=(),
                reasons=(
                    CandidateReason(
                        reason_id=stable_id("reason", source.source_id, self.strategy, "malformed"),
                        kind="code_malformed_rejection",
                        evidence_ids=tuple(obs.observation_id for obs in malformed),
                        description="malformed code cannot admit AST code candidates",
                    ),
                ),
                warnings=("malformed code observed; candidate set rejected",),
            )

        structural = _top_level_code_units(
            tuple(evidence.by_kind("code_class") + evidence.by_kind("code_function"))
        )
        if not structural:
            return self._module_candidate_set(source, evidence, policy)

        candidates: list[ChunkCandidate] = []
        reasons: list[CandidateReason] = []
        repairs: list[RepairRecord] = []
        for observation in structural:
            text = source.text_for(observation.span).strip()
            if count_tokens(text) <= policy.hard_max_tokens:
                candidate, reason = self._candidate_from_observation(source, evidence, observation, policy)
                candidates.append(candidate)
                reasons.append(reason)
                continue

            repair_spans = _repair_spans_for_observation(source, evidence, observation, policy)
            if not repair_spans:
                candidate, reason = self._candidate_from_observation(source, evidence, observation, policy)
                candidates.append(candidate)
                reasons.append(reason)
                continue

            repair = RepairRecord(
                repair_id=stable_id("repair", source.source_id, self.strategy, observation.observation_id),
                repaired_id=observation.observation_id,
                reason="oversized code unit split on AST child and source-gap spans",
                evidence_ids=(
                    observation.observation_id,
                    *tuple(obs.observation_id for obs in _child_code_units(evidence, observation.span)),
                ),
            )
            repairs.append(repair)
            for span in repair_spans:
                candidate, reason = self._candidate_from_repair_span(
                    source=source,
                    evidence=evidence,
                    span=span,
                    parent=observation,
                    policy=policy,
                    repair=repair,
                )
                candidates.append(candidate)
                reasons.append(reason)
        return ChunkCandidateSet(
            candidate_set_id=stable_id(
                "candset",
                source.source_id,
                self.strategy,
                tuple(candidate.candidate_id for candidate in candidates),
            ),
            strategy=self.strategy,
            source_id=source.source_id,
            candidates=tuple(candidates),
            reasons=tuple(reasons),
            warnings=("oversized code units repaired using AST child spans",) if repairs else (),
            repairs=tuple(repairs),
        )

    def _module_candidate_set(
        self,
        source: SourceRecord,
        evidence: EvidenceSet,
        policy: SelectionPolicy,
    ) -> ChunkCandidateSet:
        reason = CandidateReason(
            reason_id=stable_id("reason", source.source_id, self.strategy, "module"),
            kind="code_module_fallback",
            evidence_ids=tuple(obs.observation_id for obs in evidence.observations),
            description="code source has no class or function observations; module span used",
        )
        text = source.canonical_text.strip()
        candidate = ChunkCandidate(
            candidate_id=stable_id("cand", source.source_id, self.strategy, "module"),
            source_id=source.source_id,
            spans=(source.full_span(),),
            text=text,
            token_count=count_tokens(text),
            evidence_ids=reason.evidence_ids,
            reason_ids=(reason.reason_id,),
            metrics=CandidateMetrics(token_count=count_tokens(text), boundary_count=0),
            warnings=_budget_warning(text, policy),
        )
        return ChunkCandidateSet(
            candidate_set_id=stable_id("candset", source.source_id, self.strategy, "module"),
            strategy=self.strategy,
            source_id=source.source_id,
            candidates=(candidate,),
            reasons=(reason,),
        )

    def _candidate_from_observation(
        self,
        source: SourceRecord,
        evidence: EvidenceSet,
        observation: Observation,
        policy: SelectionPolicy,
    ) -> tuple[ChunkCandidate, CandidateReason]:
        related_evidence = _contained_evidence(evidence, observation.span)
        reason = CandidateReason(
            reason_id=stable_id("reason", source.source_id, self.strategy, observation.observation_id),
            kind="ast_supported_code_boundary",
            evidence_ids=related_evidence,
            description=f"AST-supported {observation.kind} boundary",
        )
        text = source.text_for(observation.span).strip()
        token_count = count_tokens(text)
        candidate = ChunkCandidate(
            candidate_id=stable_id("cand", source.source_id, self.strategy, observation.span),
            source_id=source.source_id,
            spans=(observation.span,),
            text=text,
            token_count=token_count,
            evidence_ids=related_evidence,
            reason_ids=(reason.reason_id,),
            metrics=CandidateMetrics(token_count=token_count, boundary_count=1),
            warnings=_budget_warning(text, policy),
        )
        return candidate, reason

    def _candidate_from_repair_span(
        self,
        *,
        source: SourceRecord,
        evidence: EvidenceSet,
        span: SourceSpan,
        parent: Observation,
        policy: SelectionPolicy,
        repair: RepairRecord,
    ) -> tuple[ChunkCandidate, CandidateReason]:
        contained_evidence = _strict_contained_evidence(evidence, span)
        if span.start_char == parent.span.start_char:
            evidence_ids = (parent.observation_id, *contained_evidence)
        else:
            evidence_ids = contained_evidence or (parent.observation_id,)
        reason = CandidateReason(
            reason_id=stable_id("reason", source.source_id, self.strategy, "repair", span),
            kind="ast_recursive_code_repair",
            evidence_ids=(parent.observation_id, *contained_evidence, repair.repair_id),
            description="oversized AST code unit repaired without line-window splitting",
        )
        text = source.text_for(span).strip()
        token_count = count_tokens(text)
        candidate = ChunkCandidate(
            candidate_id=stable_id("cand", source.source_id, self.strategy, "repair", span),
            source_id=source.source_id,
            spans=(span,),
            text=text,
            token_count=token_count,
            evidence_ids=evidence_ids,
            reason_ids=(reason.reason_id,),
            metrics=CandidateMetrics(token_count=token_count, boundary_count=1, repair_count=1),
            warnings=_repair_warning(text, policy),
        )
        return candidate, reason


def _top_level_code_units(observations: tuple[Observation, ...]) -> tuple[Observation, ...]:
    ordered = sorted(
        observations,
        key=lambda obs: (obs.span.start_char, -(obs.span.end_char - obs.span.start_char)),
    )
    accepted: list[Observation] = []
    for observation in ordered:
        if any(_contains(existing.span, observation.span) for existing in accepted):
            continue
        accepted.append(observation)
    return tuple(accepted)


def _repair_spans_for_observation(
    source: SourceRecord,
    evidence: EvidenceSet,
    observation: Observation,
    policy: SelectionPolicy,
) -> tuple[SourceSpan, ...]:
    children = _child_code_units(evidence, observation.span)
    if not children:
        return ()

    spans: list[SourceSpan] = []
    cursor = observation.span.start_char
    for child in children:
        if child.span.start_char > cursor:
            _append_nonempty_span(source, spans, cursor, child.span.start_char)
        child_text = source.text_for(child.span).strip()
        if count_tokens(child_text) > policy.hard_max_tokens:
            spans.extend(_repair_spans_for_observation(source, evidence, child, policy) or (child.span,))
        else:
            spans.append(child.span)
        cursor = max(cursor, child.span.end_char)
    if cursor < observation.span.end_char:
        _append_nonempty_span(source, spans, cursor, observation.span.end_char)
    return tuple(spans)


def _append_nonempty_span(
    source: SourceRecord,
    spans: list[SourceSpan],
    start_char: int,
    end_char: int,
) -> None:
    if start_char >= end_char:
        return
    if source.canonical_text[start_char:end_char].strip() or not spans:
        spans.append(span_from_chars(source, start_char, end_char))
        return
    previous = spans[-1]
    spans[-1] = span_from_chars(
        source,
        previous.start_char,
        end_char,
        line_start=previous.line_start,
    )


def _child_code_units(evidence: EvidenceSet, span: SourceSpan) -> tuple[Observation, ...]:
    contained = tuple(
        observation
        for observation in evidence.by_kind("code_class") + evidence.by_kind("code_function")
        if _contains(span, observation.span)
        and (observation.span.start_char, observation.span.end_char) != (span.start_char, span.end_char)
    )
    return _top_level_code_units(contained)


def _contained_evidence(evidence: EvidenceSet, span: SourceSpan) -> tuple[str, ...]:
    return tuple(
        obs.observation_id
        for obs in evidence.observations
        if _contains(span, obs.span) or _intersects(span, obs.span)
    )


def _strict_contained_evidence(evidence: EvidenceSet, span: SourceSpan) -> tuple[str, ...]:
    return tuple(
        obs.observation_id
        for obs in evidence.observations
        if _contains(span, obs.span)
    )


def _contains(outer: SourceSpan, inner: SourceSpan) -> bool:
    return (
        outer.source_id == inner.source_id
        and outer.start_char <= inner.start_char
        and outer.end_char >= inner.end_char
    )


def _intersects(left: SourceSpan, right: SourceSpan) -> bool:
    return (
        left.source_id == right.source_id
        and left.start_char < right.end_char
        and right.start_char < left.end_char
    )


def _budget_warning(text: str, policy: SelectionPolicy) -> tuple[str, ...]:
    if count_tokens(text) > policy.hard_max_tokens:
        return ("code unit exceeds hard token budget; AST repair or rejection required",)
    return ()


def _repair_warning(text: str, policy: SelectionPolicy) -> tuple[str, ...]:
    if count_tokens(text) > policy.hard_max_tokens:
        return ("AST repair segment still exceeds hard token budget; rejection required",)
    return ("formed by AST recursive repair",)
    return ()
