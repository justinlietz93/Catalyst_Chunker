"""Recursive fallback candidate formation."""

from __future__ import annotations

from dataclasses import dataclass
import re

from catalyst.formation.candidates.candidate_metrics import CandidateMetrics
from catalyst.formation.candidates.candidate_reason import CandidateReason
from catalyst.formation.candidates.chunk_candidate import ChunkCandidate
from catalyst.formation.candidates.chunk_candidate_set import ChunkCandidateSet
from catalyst.formation.repair.repair_record import RepairRecord
from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.observation.evidence.evidence_set import EvidenceSet
from catalyst.observation.instruments.span_tools import span_from_chars
from catalyst.observation.instruments.tokenizer_instrument import count_tokens
from catalyst.shared.ids import stable_id
from catalyst.source.records.source_record import SourceRecord
from catalyst.source.records.source_span import SourceSpan

_SENTENCE_BREAK_RE = re.compile(r"(?<=[.!?])\s+")
_WORD_RE = re.compile(r"\S+")


@dataclass(frozen=True)
class _FallbackSpan:
    span: SourceSpan
    fixed_size_slicing: bool


class RecursiveFallbackStrategy:
    """Repair oversized structural regions by recursively using smaller units."""

    strategy = "recursive_fallback"

    def form(
        self,
        source: SourceRecord,
        evidence: EvidenceSet,
        policy: SelectionPolicy,
        *,
        failed_candidate_set_id: str,
    ) -> ChunkCandidateSet:
        paragraphs = tuple(sorted(evidence.by_kind("paragraph"), key=lambda obs: obs.span.start_char))
        failed_evidence = (failed_candidate_set_id,)
        candidates: list[ChunkCandidate] = []
        reasons: list[CandidateReason] = []
        repairs: list[RepairRecord] = []

        for paragraph in paragraphs:
            text = source.text_for(paragraph.span).strip()
            if count_tokens(text) <= policy.hard_max_tokens:
                candidate, reason = self._candidate(
                    source=source,
                    spans=(paragraph.span,),
                    text=text,
                    evidence_ids=(paragraph.observation_id,),
                    fallback_evidence=failed_evidence,
                    repair_count=0,
                )
                candidates.append(candidate)
                reasons.append(reason)
                continue

            split_spans = self._split_span(source, paragraph.span, policy.hard_max_tokens)
            fixed_size_repair = None
            if any(item.fixed_size_slicing for item in split_spans):
                fixed_size_repair = RepairRecord(
                    repair_id=stable_id(
                        "repair",
                        source.source_id,
                        self.strategy,
                        paragraph.observation_id,
                        "fixed-size-token-window",
                    ),
                    repaired_id=paragraph.observation_id,
                    reason=(
                        "fixed-size token windows used after structural and sentence fallback "
                        "could not preserve hard token budget"
                    ),
                    evidence_ids=(*failed_evidence, paragraph.observation_id),
                )
                repairs.append(fixed_size_repair)

            for item in split_spans:
                text = source.text_for(item.span).strip()
                candidate, reason = self._candidate(
                    source=source,
                    spans=(item.span,),
                    text=text,
                    evidence_ids=(paragraph.observation_id,),
                    fallback_evidence=failed_evidence,
                    repair_count=1,
                    fixed_size_slicing=item.fixed_size_slicing,
                    repair=fixed_size_repair if item.fixed_size_slicing else None,
                )
                candidates.append(candidate)
                reasons.append(reason)

        return ChunkCandidateSet(
            candidate_set_id=stable_id(
                "candset",
                source.source_id,
                self.strategy,
                failed_candidate_set_id,
                tuple(candidate.candidate_id for candidate in candidates),
            ),
            strategy=self.strategy,
            source_id=source.source_id,
            candidates=tuple(candidates),
            reasons=tuple(reasons),
            warnings=(f"fallback after candidate set {failed_candidate_set_id}",),
            repairs=tuple(repairs),
        )

    def _candidate(
        self,
        *,
        source: SourceRecord,
        spans: tuple[SourceSpan, ...],
        text: str,
        evidence_ids: tuple[str, ...],
        fallback_evidence: tuple[str, ...],
        repair_count: int,
        fixed_size_slicing: bool = False,
        repair: RepairRecord | None = None,
    ) -> tuple[ChunkCandidate, CandidateReason]:
        kind = (
            "fixed_size_token_window_after_recursive_fallback"
            if fixed_size_slicing
            else "recursive_fallback_after_structural_failure"
        )
        description = (
            "fixed-size token window used only after structural and sentence fallback failed"
            if fixed_size_slicing
            else "recursive fallback used after structural candidate set failed hard gates"
        )
        reason_evidence = (*evidence_ids, *fallback_evidence)
        if repair is not None:
            reason_evidence = (*reason_evidence, repair.repair_id)
        reason = CandidateReason(
            reason_id=stable_id("reason", source.source_id, self.strategy, spans, fallback_evidence),
            kind=kind,
            evidence_ids=reason_evidence,
            description=description,
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
                repair_count=repair_count,
            ),
            warnings=_fallback_warnings(repair_count, fixed_size_slicing),
        )
        return candidate, reason

    def _split_span(
        self,
        source: SourceRecord,
        span: SourceSpan,
        hard_max_tokens: int,
    ) -> tuple[_FallbackSpan, ...]:
        text = source.text_for(span)
        sentence_spans = self._sentence_spans(source, span, text)
        output: list[_FallbackSpan] = []
        current: list[SourceSpan] = []

        def flush() -> None:
            if current:
                output.append(_FallbackSpan(_merge_spans(source, tuple(current)), False))
                current.clear()

        for sentence_span in sentence_spans:
            sentence_text = source.text_for(sentence_span).strip()
            if count_tokens(sentence_text) > hard_max_tokens:
                flush()
                output.extend(self._word_windows(source, sentence_span, hard_max_tokens))
                continue
            next_spans = (*current, sentence_span)
            next_text = source.canonical_text[next_spans[0].start_char : next_spans[-1].end_char]
            if current and count_tokens(next_text) > hard_max_tokens:
                flush()
            current.append(sentence_span)
        flush()
        return tuple(output)

    def _sentence_spans(
        self,
        source: SourceRecord,
        span: SourceSpan,
        text: str,
    ) -> tuple[SourceSpan, ...]:
        parts = _SENTENCE_BREAK_RE.split(text)
        spans: list[SourceSpan] = []
        cursor = span.start_char
        for part in parts:
            if not part:
                continue
            start = source.canonical_text.find(part, cursor, span.end_char)
            if start < 0:
                continue
            end = start + len(part)
            while end < span.end_char and source.canonical_text[end].isspace():
                end += 1
            spans.append(span_from_chars(source, start, end))
            cursor = end
        return tuple(spans) or (span,)

    def _word_windows(
        self,
        source: SourceRecord,
        span: SourceSpan,
        hard_max_tokens: int,
    ) -> tuple[_FallbackSpan, ...]:
        text = source.text_for(span)
        matches = list(_WORD_RE.finditer(text))
        windows: list[_FallbackSpan] = []
        for index in range(0, len(matches), hard_max_tokens):
            group = matches[index : index + hard_max_tokens]
            if not group:
                continue
            start = span.start_char if index == 0 else windows[-1].span.end_char
            next_group = matches[index + hard_max_tokens : index + hard_max_tokens + 1]
            if next_group:
                end = span.start_char + next_group[0].start()
            else:
                end = span.end_char
            windows.append(_FallbackSpan(span_from_chars(source, start, end), True))
        return tuple(windows)


def _fallback_warnings(repair_count: int, fixed_size_slicing: bool) -> tuple[str, ...]:
    if fixed_size_slicing:
        return (
            "formed by recursive fallback",
            "fixed-size token window used after structural and sentence fallback",
        )
    if repair_count:
        return ("formed by recursive fallback",)
    return ()


def _merge_spans(source: SourceRecord, spans: tuple[SourceSpan, ...]) -> SourceSpan:
    return span_from_chars(
        source,
        min(span.start_char for span in spans),
        max(span.end_char for span in spans),
        line_start=spans[0].line_start,
        line_end=spans[-1].line_end,
    )
