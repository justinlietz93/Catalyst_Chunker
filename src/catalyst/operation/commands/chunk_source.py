"""Chunk source operation."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.formation.selection.selector import SelectionResult, select_candidate_set
from catalyst.formation.strategies.paragraph_group_strategy import ParagraphGroupStrategy
from catalyst.invariant.checks.rejection_visibility_check import check_rejection_visibility
from catalyst.invariant.checks.source_lineage_check import check_source_lineage
from catalyst.invariant.checks.token_budget_check import check_token_budget
from catalyst.invariant.ledger.invariant_ledger import InvariantLedger
from catalyst.observation.evidence.evidence_set import EvidenceSet
from catalyst.observation.instruments.collect import observe_source
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
    candidate_set = ParagraphGroupStrategy().form(source, evidence, active_policy)
    selection = select_candidate_set((candidate_set,), active_policy)
    chunks = _admit_chunks(selection)
    invariant_results = (
        check_source_lineage(chunks),
        check_token_budget(chunks, active_policy.hard_max_tokens),
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
