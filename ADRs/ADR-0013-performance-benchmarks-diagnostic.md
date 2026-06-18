# ADR-0013: Performance Benchmarks Are Diagnostic Evidence

## Status

Accepted

## Context

Catalyst should be practical as both a standalone tool and an internal library. Users need to know how chunking behaves on large prose, code, Markdown, noisy text, and adversarial inputs.

Performance matters, but early strict timing gates can become noisy across machines and can distort design by optimizing before the invariant surface is stable.

## Decision

Catalyst will add performance benchmarks as diagnostic evidence first.

Benchmark records may measure wall time, source size, chunk count, token count, strategy identity, repair count, invariant status, and peak memory where practical. These records do not become admission invariants unless a later ADR promotes a specific benchmark condition.

CI may run small benchmark smoke checks, but strict latency or memory gates are deferred.

## Evidence

- Catalyst already emits source measures and diagnostic benchmark-like records for retrieval and context recovery.
- The package is intended for agentic applications where throughput and memory behavior affect usability.
- Reproducible performance baselines require representative fixtures and stable measurement scope.

## Alternatives Considered

- Add no performance evidence: rejected because users need scale expectations.
- Add hard CI latency gates immediately: rejected because machine variance would create noisy failures.
- Add a heavy benchmark dependency to runtime: rejected because benchmarking belongs in development tooling, not core execution.

## Consequences

Performance benchmark output must be clearly marked as diagnostic.

Benchmarks should prefer standard-library measurement unless an optional development dependency is justified.

Optimization work should cite benchmark evidence and must not weaken source invariants.

## Implementation Acceptance Criteria

- Benchmark fixtures cover at least large prose, code, Markdown, and long atomic text shapes.
- Benchmark records include schema version, source measures, strategy identity, chunk count, token count, repair count, invariant summary, and elapsed time.
- Peak memory is recorded where practical without adding required runtime dependencies.
- CI verifies that small benchmark commands complete.
- Documentation warns that diagnostic timing is machine-dependent.

## Review Trigger

Revisit this ADR if benchmark variance prevents useful comparison or if users need formal performance budgets for a supported deployment target.

