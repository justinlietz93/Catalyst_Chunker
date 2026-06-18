"""Chunk parsed code from AST evidence."""

from __future__ import annotations

from dataclasses import dataclass

from catalyst.boundary.ports.parsed_code import ParsedCode
from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.formation.selection.selector import SelectionResult, select_candidate_set
from catalyst.formation.strategies.ast_code_strategy import AstCodeStrategy
from catalyst.invariant.checks.offset_reversibility_check import check_offset_reversibility
from catalyst.invariant.checks.rejection_visibility_check import check_rejection_visibility
from catalyst.invariant.checks.source_coverage_check import check_source_coverage
from catalyst.invariant.checks.source_lineage_check import check_source_lineage
from catalyst.invariant.checks.token_budget_check import check_token_budget
from catalyst.invariant.ledger.invariant_ledger import InvariantLedger
from catalyst.projection.chunks.accepted_chunk import AcceptedChunk
from catalyst.projection.chunks.chunk_graph import ChunkGraph
from catalyst.projection.chunks.chunk_relation import ChunkRelation
from catalyst.shared.errors import InvariantViolation
from catalyst.shared.ids import stable_id


@dataclass(frozen=True)
class ChunkCodeResult:
    """Result of admitting a code chunk graph."""

    parsed: ParsedCode
    selection: SelectionResult
    graph: ChunkGraph
    invariant_ledger: InvariantLedger


def chunk_parsed_code(
    parsed: ParsedCode,
    *,
    policy: SelectionPolicy | None = None,
) -> ChunkCodeResult:
    """Form an admitted code chunk graph from AST observations."""

    active_policy = policy or SelectionPolicy()
    candidate_set = AstCodeStrategy().form(parsed.source, parsed.evidence, active_policy)
    selection = select_candidate_set((candidate_set,), active_policy)
    chunks = _admit_code_chunks(selection)
    required_spans = _required_code_spans(parsed, chunks)
    all_chunk_spans = tuple(span for chunk in chunks for span in chunk.spans)
    invariant_results = (
        check_source_coverage(required_spans=required_spans, chunks=chunks),
        check_source_lineage(chunks),
        check_offset_reversibility(parsed.source, all_chunk_spans),
        check_token_budget(chunks, active_policy.hard_max_tokens),
        check_rejection_visibility(selection.rejections),
    )
    ledger = InvariantLedger(invariant_results)
    if not ledger.passed:
        messages = "; ".join(result.message for result in ledger.violations())
        raise InvariantViolation(messages)

    graph = ChunkGraph(
        graph_id=stable_id("graph", parsed.source.source_id, "code", tuple(chunk.chunk_id for chunk in chunks)),
        source_id=parsed.source.source_id,
        chunks=chunks,
        relations=_code_relations(parsed, chunks),
        formation_policy_id=selection.decision.policy_id,
        invariant_result_ids=tuple(result.result_id for result in ledger.results),
        decision_record_ids=(selection.decision.decision_id,),
    )
    return ChunkCodeResult(
        parsed=parsed,
        selection=selection,
        graph=graph,
        invariant_ledger=ledger,
    )


def _admit_code_chunks(selection: SelectionResult) -> tuple[AcceptedChunk, ...]:
    return tuple(
        AcceptedChunk(
            chunk_id=stable_id("chk", candidate.candidate_id),
            source_id=candidate.source_id,
            spans=candidate.spans,
            text=candidate.text,
            token_count=candidate.token_count,
            chunk_kind="code",
            candidate_set_id=selection.accepted.candidate_set_id,
            evidence_ids=candidate.evidence_ids,
            warning_ids=candidate.warnings,
        )
        for candidate in selection.accepted.candidates
    )


def _required_code_spans(parsed: ParsedCode, chunks: tuple[AcceptedChunk, ...]) -> tuple[object, ...]:
    structural = parsed.evidence.by_kind("code_class") + parsed.evidence.by_kind("code_function")
    if structural:
        return tuple(observation.span for observation in structural)
    return tuple(span for chunk in chunks for span in chunk.spans)


def _code_relations(parsed: ParsedCode, chunks: tuple[AcceptedChunk, ...]) -> tuple[ChunkRelation, ...]:
    relations = list(_adjacency_relations(chunks))
    definitions = _definition_chunks(parsed, chunks)
    module_imports = tuple(parsed.evidence.by_kind("code_import"))
    for _name, (chunk_id, observation_id) in definitions.items():
        relations.append(ChunkRelation(chunk_id, chunk_id, "defines", (observation_id,)))
    for chunk in chunks:
        for import_observation in module_imports:
            relations.append(
                ChunkRelation(
                    chunk.chunk_id,
                    chunk.chunk_id,
                    "code_imports_for",
                    (import_observation.observation_id,),
                )
            )
        evidence = [
            observation
            for observation in parsed.evidence.observations
            if any(_span_contains(span, observation.span) for span in chunk.spans)
        ]
        for observation in evidence:
            if observation.kind == "code_call":
                target = definitions.get(str(observation.payload.get("call", "")))
                if target and target[0] != chunk.chunk_id:
                    relations.append(
                        ChunkRelation(
                            chunk.chunk_id,
                            target[0],
                            "code_calls",
                            (observation.observation_id,),
                        )
                    )
    return tuple(relations)


def _definition_chunks(parsed: ParsedCode, chunks: tuple[AcceptedChunk, ...]) -> dict[str, tuple[str, str]]:
    definitions: dict[str, tuple[str, str]] = {}
    for observation in parsed.evidence.observations:
        if observation.kind not in {"code_class", "code_function"}:
            continue
        name = observation.payload.get("name")
        if not name:
            continue
        matched = False
        for chunk in chunks:
            if any(_span_contains(span, observation.span) for span in chunk.spans):
                definitions[str(name)] = (chunk.chunk_id, observation.observation_id)
                matched = True
                break
        if matched:
            continue
        for chunk in chunks:
            if any(_span_intersects(span, observation.span) for span in chunk.spans):
                definitions[str(name)] = (chunk.chunk_id, observation.observation_id)
                break
    return definitions


def _adjacency_relations(chunks: tuple[AcceptedChunk, ...]) -> tuple[ChunkRelation, ...]:
    relations: list[ChunkRelation] = []
    for index, chunk in enumerate(chunks):
        if index > 0:
            relations.append(ChunkRelation(chunk.chunk_id, chunks[index - 1].chunk_id, "previous_sibling"))
        if index + 1 < len(chunks):
            relations.append(ChunkRelation(chunk.chunk_id, chunks[index + 1].chunk_id, "next_sibling"))
    return tuple(relations)


def _span_contains(outer: object, inner: object) -> bool:
    return (
        getattr(outer, "source_id") == getattr(inner, "source_id")
        and getattr(outer, "start_char") <= getattr(inner, "start_char")
        and getattr(outer, "end_char") >= getattr(inner, "end_char")
    )


def _span_intersects(left: object, right: object) -> bool:
    return (
        getattr(left, "source_id") == getattr(right, "source_id")
        and getattr(left, "start_char") < getattr(right, "end_char")
        and getattr(right, "start_char") < getattr(left, "end_char")
    )
