"""Structure-first paragraph grouping."""

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


class ParagraphGroupStrategy:
    """Form prose chunk candidates from paragraph observations."""

    strategy = "paragraph_group"

    def form(
        self,
        source: SourceRecord,
        evidence: EvidenceSet,
        policy: SelectionPolicy,
    ) -> ChunkCandidateSet:
        paragraphs = tuple(sorted(evidence.by_kind("paragraph"), key=lambda obs: obs.span.start_char))
        if not paragraphs:
            return ChunkCandidateSet(
                candidate_set_id=stable_id("candset", source.source_id, self.strategy, "empty"),
                strategy=self.strategy,
                source_id=source.source_id,
                candidates=(),
                reasons=(),
                warnings=("no paragraph observations available",),
            )

        candidates: list[ChunkCandidate] = []
        reasons: list[CandidateReason] = []
        group: list[Observation] = []

        def flush() -> None:
            if not group:
                return
            candidate, reason = self._candidate_from_group(source, tuple(group), policy)
            candidates.append(candidate)
            reasons.append(reason)
            group.clear()

        for paragraph in paragraphs:
            next_text = self._join_text(source, (*group, paragraph))
            if group and count_tokens(next_text) > policy.target_tokens:
                flush()
            group.append(paragraph)

        flush()
        candidate_set_id = stable_id(
            "candset",
            source.source_id,
            self.strategy,
            tuple(candidate.candidate_id for candidate in candidates),
        )
        return ChunkCandidateSet(
            candidate_set_id=candidate_set_id,
            strategy=self.strategy,
            source_id=source.source_id,
            candidates=tuple(candidates),
            reasons=tuple(reasons),
        )

    def _candidate_from_group(
        self,
        source: SourceRecord,
        observations: tuple[Observation, ...],
        policy: SelectionPolicy,
    ) -> tuple[ChunkCandidate, CandidateReason]:
        spans = tuple(obs.span for obs in observations)
        text = self._join_spans(source, spans)
        token_count = count_tokens(text)
        evidence_ids = tuple(obs.observation_id for obs in observations)
        reason = CandidateReason(
            reason_id=stable_id("reason", source.source_id, self.strategy, evidence_ids),
            kind="structure_first_paragraph_group",
            evidence_ids=evidence_ids,
            description="paragraph observations grouped before token fallback",
        )
        warnings = ()
        if token_count > policy.hard_max_tokens:
            warnings = ("candidate exceeds hard token budget and requires repair",)
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
            warnings=warnings,
        )
        return candidate, reason

    def _join_text(self, source: SourceRecord, observations: tuple[Observation, ...]) -> str:
        return self._join_spans(source, tuple(obs.span for obs in observations))

    def _join_spans(self, source: SourceRecord, spans: tuple[SourceSpan, ...]) -> str:
        if not spans:
            return ""
        start = min(span.start_char for span in spans)
        end = max(span.end_char for span in spans)
        return source.canonical_text[start:end].strip()
