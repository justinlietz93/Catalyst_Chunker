# ADR-0012: Retrieval Evaluation Uses Held-Out Metrics

## Status

Accepted

## Context

Catalyst already has retrieval sanity and context-recovery diagnostics. These records compare strategy output, expected terms, hard invariant status, chunk cost, and relation-window recovery.

The next evaluation layer should test retrieval usefulness more directly. A chunker intended for retrieval and agentic context curation needs held-out query fixtures and explicit metrics such as recall@k and MRR.

## Decision

Catalyst will deepen retrieval evaluation with held-out query metrics.

The default evaluator must remain deterministic and dependency-light. A lexical baseline is admitted as the default local evaluator. Embedding, vector database, or model-backed retrieval experiments may be added later through boundary adapters or external examples.

Retrieval metrics are diagnostic evidence. They cannot override hard invariants.

## Evidence

- ADR-0007 requires retrieval context recovery without blanket overlap.
- Existing retrieval sanity evaluation already records strategy, invariant status, matched terms, missing terms, and cost.
- Held-out query metrics make strategy tradeoffs more visible than one-off term coverage.

## Alternatives Considered

- Use only existing retrieval sanity fixtures: rejected because they do not fully express ranking quality.
- Make an embedding model the default evaluator: rejected because Catalyst must remain usable without model dependencies.
- Let retrieval score choose chunks that violate hard invariants: rejected because retrieval usefulness cannot override source truth.

## Consequences

Benchmark fixtures need explicit relevant chunks, relevant source spans, or expected answer-support terms.

Evaluation output must identify the strategy, metric values, cost measures, and invariant status.

Optional retrieval backends must not become required package dependencies.

## Implementation Acceptance Criteria

- Held-out retrieval fixtures include query text and expected relevant evidence.
- Evaluation reports recall@k and MRR for at least one deterministic local ranking method.
- Evaluation reports chunk count, token count, strategy identity, and invariant pass/fail state.
- Strategy comparison includes structure-first, semantic refinement where enabled, and fallback behavior where applicable.
- Documentation states that metrics are diagnostic and cannot admit invariant-violating chunks.

## Review Trigger

Revisit this ADR if benchmark results show that current metrics do not predict downstream retrieval quality or if a source family needs a different no-dependency scoring baseline.

