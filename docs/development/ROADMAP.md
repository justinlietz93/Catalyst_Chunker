# Roadmap

This roadmap sequences the next Catalyst Chunker work after the `0.1.3` PyPI release and the start of the `0.1.4` development line.

Roadmap items are not admission proof by themselves. Each item must land through tests, governance checks, and the relevant ADR acceptance criteria.

## Current Release Line

`0.1.4` is the active development line.

## Priority Principles

- Keep Catalyst usable without LLMs, embeddings, vector databases, or observability services.
- Keep downstream model/provider translation at boundary adapters.
- Treat benchmarks as diagnostic evidence unless an ADR promotes a benchmark condition into an invariant.
- Prefer deterministic fixtures and local tests before external integrations.
- Do not add release automation in this line. Manual PyPI/TestPyPI release control remains sufficient for now.

## Phase 1: Invariant Test Hardening

Related ADR: [ADR-0011](../../ADRs/ADR-0011-property-based-invariant-fuzzing.md)

### Task: Add property-based invariant tests

Steps:

1. Add a bounded property-test tool to the development dependency group.
2. Generate source inputs covering ASCII, Unicode, whitespace, punctuation, empty-like content, and long atomic runs.
3. Check stable ID determinism, offset reversibility, source coverage, lineage preservation, and token-budget behavior across generated inputs.
4. Convert any discovered minimal failure into a named regression fixture.
5. Keep generated tests deterministic enough for CI.

## Phase 2: Retrieval Evaluation

Related ADR: [ADR-0012](../../ADRs/ADR-0012-retrieval-evaluation-heldout-metrics.md)

### Task: Deepen retrieval benchmark evidence

Steps:

1. Extend retrieval fixtures with held-out queries and expected relevant chunks or source spans.
2. Add deterministic lexical scoring as the default no-dependency retrieval baseline.
3. Report recall@k, MRR, answer-context adequacy, chunk count, token count, and strategy identity.
4. Compare admitted strategies without letting retrieval score override hard invariants.
5. Document how optional embedding or vector-store experiments can run outside the core benchmark.

## Phase 3: Performance Evidence

Related ADR: [ADR-0013](../../ADRs/ADR-0013-performance-benchmarks-diagnostic.md)

### Task: Add diagnostic performance benchmarks

Steps:

1. Add benchmark fixtures for large prose, code, Markdown, and adversarial text shapes.
2. Measure wall time, peak memory where practical, source size, chunk count, token count, strategy, and invariant summary.
3. Emit a versioned diagnostic benchmark record.
4. Add a CI smoke check that benchmark commands complete on small fixtures.
5. Defer strict latency or memory gates until stable baselines exist across machines.

## Phase 4: Generic Retrieval Ingestion Examples

Related ADR: [ADR-0014](../../ADRs/ADR-0014-retrieval-ingestion-examples-boundary-external.md)

### Task: Provide app-neutral ingestion examples

Steps:

1. Add examples that map retrieval projections or chunk graphs into a simple ingestion DTO.
2. Include source ID, chunk ID, text, spans, schema version, metadata, and relation references.
3. Keep vector database, Crux Studio, Neuroca, and provider-specific naming out of core types.
4. Add tests that examples fail loudly if required projection fields drift.
5. Document where consuming applications should apply provider-token and vector-store mappings.

## Phase 5: Optional Telemetry Adapters

Related ADR: [ADR-0015](../../ADRs/ADR-0015-telemetry-adapters-optional.md)

### Task: Make telemetry observable without making it required

Steps:

1. Document stable telemetry event names and payload shapes.
2. Add a no-op or in-memory telemetry example for tests and local use.
3. Add optional Prometheus or OpenTelemetry adapters only behind extras if they are admitted.
4. Ensure telemetry failures never change chunk admission.
5. Avoid emitting full source text by default.

## Out Of Scope For 0.1.4

- Automatic PyPI publishing.
- Required vector database integrations.
- Required LLM, embedding, or provider tokenizer dependencies.
- Metrics or benchmark scores that override hard invariants.
- App-specific core DTOs for a single downstream product.

