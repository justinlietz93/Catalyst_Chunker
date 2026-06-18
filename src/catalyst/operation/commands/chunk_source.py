"""Chunk source operation."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.formation.selection.selector import SelectionResult, select_candidate_set
from catalyst.formation.strategies.paragraph_group_strategy import ParagraphGroupStrategy
from catalyst.formation.strategies.recursive_fallback_strategy import RecursiveFallbackStrategy
from catalyst.formation.strategies.semantic_refinement_strategy import SemanticRefinementStrategy
from catalyst.invariant.checks.fallback_evidence_check import check_fallback_evidence
from catalyst.invariant.checks.offset_reversibility_check import check_offset_reversibility
from catalyst.invariant.checks.rejection_visibility_check import check_rejection_visibility
from catalyst.invariant.checks.source_coverage_check import check_source_coverage
from catalyst.invariant.checks.source_lineage_check import check_source_lineage
from catalyst.invariant.checks.token_budget_check import check_token_budget
from catalyst.invariant.ledger.invariant_ledger import InvariantLedger
from catalyst.observation.evidence.evidence_set import EvidenceSet
from catalyst.observation.instruments.collect import observe_source
from catalyst.observation.instruments.semantic_shift_instrument import SemanticShiftInstrument
from catalyst.projection.chunks.accepted_chunk import AcceptedChunk
from catalyst.projection.chunks.chunk_graph import ChunkGraph
from catalyst.projection.chunks.chunk_relation import ChunkRelation
from catalyst.shared.errors import InvariantViolation
from catalyst.shared.ids import stable_id
from catalyst.source.normalization.reversible_normalizer import ReversibleNormalizer
from catalyst.source.records.source_record import SourceRecord


@dataclass(frozen=True)
class ChunkSourceResult:
    """Result of forming an admitted chunk graph."""

    source: SourceRecord
    evidence: EvidenceSet
    selection: SelectionResult
    graph: ChunkGraph
    invariant_ledger: InvariantLedger


def chunk_source(
    raw_bytes: bytes,
    *,
    location: str | None = None,
    source_kind: str = "markdown",
    policy: SelectionPolicy | None = None,
) -> ChunkSourceResult:
    """Form an admitted chunk graph from source bytes."""

    active_policy = policy or SelectionPolicy()
    source = SourceRecord.from_bytes(
        raw_bytes,
        source_kind=source_kind,
        location=location,
    )
    source, _trace = ReversibleNormalizer().normalize(source)
    evidence = observe_source(source)
    if active_policy.allow_semantic_refinement:
        semantic_observations = SemanticShiftInstrument().observe(source)
        evidence = EvidenceSet(
            source_id=evidence.source_id,
            observations=(*evidence.observations, *semantic_observations),
        )
    return chunk_observed_source(source, evidence, policy=active_policy)


def chunk_observed_source(
    source: SourceRecord,
    evidence: EvidenceSet,
    *,
    policy: SelectionPolicy | None = None,
) -> ChunkSourceResult:
    """Form chunks from a source that already has observations."""

    active_policy = policy or SelectionPolicy()
    candidate_set = ParagraphGroupStrategy().form(source, evidence, active_policy)
    semantic_set = SemanticRefinementStrategy().form(
        source,
        evidence,
        active_policy,
        structural_candidate_set=candidate_set,
    )
    fallback_set = RecursiveFallbackStrategy().form(
        source,
        evidence,
        active_policy,
        failed_candidate_set_id=candidate_set.candidate_set_id,
    )
    candidate_sets = (
        (semantic_set, candidate_set, fallback_set)
        if semantic_set.candidates
        else (candidate_set, fallback_set)
    )
    selection = select_candidate_set(candidate_sets, active_policy)
    chunks = _admit_chunks(selection)
    required_spans = tuple(observation.span for observation in evidence.by_kind("paragraph"))
    all_chunk_spans = tuple(span for chunk in chunks for span in chunk.spans)
    invariant_results = (
        check_source_coverage(required_spans=required_spans, chunks=chunks),
        check_source_lineage(chunks),
        check_offset_reversibility(source, all_chunk_spans),
        check_token_budget(chunks, active_policy.hard_max_tokens),
        check_fallback_evidence(candidate_sets),
        check_rejection_visibility(selection.rejections),
    )
    ledger = InvariantLedger(results=invariant_results)
    if not ledger.passed:
        messages = "; ".join(result.message for result in ledger.violations())
        raise InvariantViolation(messages)

    graph = ChunkGraph(
        graph_id=stable_id("graph", source.source_id, tuple(chunk.chunk_id for chunk in chunks)),
        source_id=source.source_id,
        chunks=chunks,
        relations=_adjacency_relations(chunks),
        formation_policy_id=selection.decision.policy_id,
        invariant_result_ids=tuple(result.result_id for result in ledger.results),
        decision_record_ids=(selection.decision.decision_id,),
    )
    return ChunkSourceResult(
        source=source,
        evidence=evidence,
        selection=selection,
        graph=graph,
        invariant_ledger=ledger,
    )


def _admit_chunks(selection: SelectionResult) -> tuple[AcceptedChunk, ...]:
    chunks: list[AcceptedChunk] = []
    for candidate in selection.accepted.candidates:
        chunks.append(
            AcceptedChunk(
                chunk_id=stable_id("chk", candidate.candidate_id),
                source_id=candidate.source_id,
                spans=candidate.spans,
                text=candidate.text,
                token_count=candidate.token_count,
                chunk_kind="prose",
                candidate_set_id=selection.accepted.candidate_set_id,
                evidence_ids=candidate.evidence_ids,
                warning_ids=candidate.warnings,
            )
        )
    return tuple(chunks)


def _adjacency_relations(chunks: tuple[AcceptedChunk, ...]) -> tuple[ChunkRelation, ...]:
    relations: list[ChunkRelation] = []
    for index, chunk in enumerate(chunks):
        if index > 0:
            relations.append(
                ChunkRelation(
                    source_chunk_id=chunk.chunk_id,
                    target_chunk_id=chunks[index - 1].chunk_id,
                    relation_kind="previous_sibling",
                )
            )
        if index + 1 < len(chunks):
            relations.append(
                ChunkRelation(
                    source_chunk_id=chunk.chunk_id,
                    target_chunk_id=chunks[index + 1].chunk_id,
                    relation_kind="next_sibling",
                )
            )
    return tuple(relations)
