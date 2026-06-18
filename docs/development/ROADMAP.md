# Roadmap

This roadmap sequences the next Catalyst Chunker work after the `0.1.3` PyPI release and the `0.1.4` planning line.

Roadmap items are not admission proof by themselves. Each item must land through tests, governance checks, and the relevant ADR acceptance criteria.

## Current Release Line

`0.1.8` is the active development line.

## Priority Principles

- Keep Catalyst usable without LLMs, embeddings, vector databases, or observability services.
- Keep downstream model/provider translation at boundary adapters.
- Treat benchmarks as diagnostic evidence unless an ADR promotes a benchmark condition into an invariant.
- Prefer deterministic fixtures and local tests before external integrations.
- Do not add release automation in this line. Manual PyPI/TestPyPI release control remains sufficient for now.

## Phase 1: Invariant Test Hardening

Status: implemented in `0.1.5`.

Related ADR: [ADR-0011](../../ADRs/ADR-0011-property-based-invariant-fuzzing.md)

### Task: Add property-based invariant tests

Steps:

1. Add a bounded property-test tool to the development dependency group.
2. Generate source inputs covering ASCII, Unicode, whitespace, punctuation, empty-like content, and long atomic runs.
3. Check stable ID determinism, offset reversibility, source coverage, lineage preservation, and token-budget behavior across generated inputs.
4. Convert any discovered minimal failure into a named regression fixture.
5. Keep generated tests deterministic enough for CI.

## Phase 2: Retrieval Evaluation

Status: implemented in `0.1.6`.

Related ADR: [ADR-0012](../../ADRs/ADR-0012-retrieval-evaluation-heldout-metrics.md)

### Task: Deepen retrieval benchmark evidence

Steps:

1. Extend retrieval fixtures with held-out queries and expected relevant chunks or source spans.
2. Add deterministic lexical scoring as the default no-dependency retrieval baseline.
3. Report recall@k, MRR, answer-context adequacy, chunk count, token count, and strategy identity.
4. Compare admitted strategies without letting retrieval score override hard invariants.
5. Document how optional embedding or vector-store experiments can run outside the core benchmark.

## Phase 3: Performance Evidence

Status: implemented in `0.1.7`.

Related ADR: [ADR-0013](../../ADRs/ADR-0013-performance-benchmarks-diagnostic.md)

### Task: Add diagnostic performance benchmarks

Steps:

1. Add benchmark fixtures for large prose, code, Markdown, and adversarial text shapes.
2. Measure wall time, peak memory where practical, source size, chunk count, token count, strategy, and invariant summary.
3. Emit a versioned diagnostic benchmark record.
4. Add a CI smoke check that benchmark commands complete on small fixtures.
5. Defer strict latency or memory gates until stable baselines exist across machines.

## Phase 4: Generic Retrieval Ingestion Examples

Status: implemented in `0.1.8`.

Related ADR: [ADR-0014](../../ADRs/ADR-0014-retrieval-ingestion-examples-boundary-external.md)

### Task: Provide app-neutral ingestion examples

Steps:

1. Add examples that map retrieval projections or chunk graphs into a simple ingestion DTO.
2. Include source ID, chunk ID, text, spans, schema version, metadata, and relation references.
3. Keep vector database, Crux Studio, Neuroca, and provider-specific naming out of core types.
4. Add tests that examples fail loudly if required projection fields drift.
5. Document where consuming applications should apply provider-token and vector-store mappings.

## Phase 5: Optional Telemetry Adapters

Status: implemented in `0.1.8`.

Related ADR: [ADR-0015](../../ADRs/ADR-0015-telemetry-adapters-optional.md)

### Task: Make telemetry observable without making it required

Steps:

1. Document stable telemetry event names and payload shapes.
2. Add a no-op or in-memory telemetry example for tests and local use.
3. Add optional Prometheus or OpenTelemetry adapters only behind extras if they are admitted.
4. Ensure telemetry failures never change chunk admission.
5. Avoid emitting full source text by default.

## Phase 6: Messy Source-Family Proof Fixtures

Status: planned.

Related ADR: [ADR-0016](../../ADRs/ADR-0016-messy-source-family-fixtures.md)

### Task: Add contradiction fixtures for noisy source families

Steps:

1. Add fixtures for OCR noise, multi-column extraction, tables, malformed Markdown, and unusual code shapes.
2. Declare the source-family risk each fixture tests.
3. Prove lawful admission or inspectable rejection/repair evidence.
4. Keep default fixtures dependency-free.
5. Preserve source lineage and offset reversibility across all admitted chunks.

## Phase 7: Admission Explanation

Status: planned.

Related ADR: [ADR-0017](../../ADRs/ADR-0017-admission-explanation-trace.md)

### Task: Explain admitted chunks through existing evidence

Steps:

1. Add a versioned admission explanation projection or CLI path.
2. Link chunk ID to source spans, observations, candidate reasons, selection decision, and invariant results.
3. Distinguish admitted evidence from rejected or repaired alternatives.
4. Keep explanation output source-preserving and LLM-free.
5. Add tests that fail if explanation drops lineage or invariant references.

## Phase 8: Relation Evidence Refinement

Status: planned.

Related ADR: [ADR-0018](../../ADRs/ADR-0018-relation-evidence-before-relation-scoring.md)

### Task: Make relation formation evidence inspectable

Steps:

1. Audit relation kinds and identify which require source evidence.
2. Add evidence IDs to dependency-like relations where source evidence exists.
3. Keep adjacency relations distinct from evidence-bearing semantic/dependency relations.
4. Expose relation evidence in projections.
5. Defer relation scoring until evidence-bearing relation fixtures exist.

## Phase 9: Document Adapter Contradiction Tests

Status: planned.

Related ADR: [ADR-0019](../../ADRs/ADR-0019-document-adapter-contradiction-fixtures.md)

### Task: Prove document adapters stay at the boundary

Steps:

1. Add fixtures for table continuation, OCR hyphenation/noise, layout ambiguity, and false headings where practical.
2. Verify adapter observations preserve source IDs and reversible spans.
3. Prove false structure becomes rejected, repaired, or inspectable.
4. Keep optional adapter dependency tests isolated.
5. Continue running boundary purity governance.

## Out Of Scope For This Roadmap

- Automatic PyPI publishing.
- Required vector database integrations.
- Required LLM, embedding, or provider tokenizer dependencies.
- Metrics or benchmark scores that override hard invariants.
- App-specific core DTOs for a single downstream product.
