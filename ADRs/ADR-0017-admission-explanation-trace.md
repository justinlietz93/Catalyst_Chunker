# ADR-0017: Admission Explanation Traces Evidence To Decision

## Status

Accepted

## Context

Catalyst already exposes audit records, candidate evaluation, rejection records, and invariant ledgers. These are enough for correctness, but a caller may still need a direct explanation of why one admitted chunk exists.

The explanation should not invent a new decision layer. It should trace existing records from source span to observation, candidate reason, selection decision, and invariant result.

## Decision

Catalyst will add an admission explanation path that traces admitted chunks back to their evidence and decision chain.

The explanation is a projection over existing truth. It does not admit chunks, alter candidate selection, or summarize away contradictions.

## Evidence

- ADR-0010 requires rejected candidates to remain inspectable.
- ADR-0009 requires public projections to be versioned.
- The current CLI can explain one retrieval record, but not the full admission chain.

## Alternatives Considered

- Expand retrieval records with all audit detail: rejected because retrieval records should remain compact.
- Ask an LLM to explain chunk admission: rejected because model explanation is not source truth.
- Keep only audit JSON: rejected because audit records are complete but not caller-ergonomic for one chunk.

## Consequences

Admission explanation should reuse existing source spans, observations, candidate reasons, decision records, and invariant results.

The projection must be versioned if emitted as machine-readable public output.

The CLI may expose explanation for one chunk without changing retrieval output.

## Implementation Acceptance Criteria

- Explanation output links one admitted chunk to source spans, evidence IDs, candidate reason IDs, selection decision ID, and invariant result IDs.
- Explanation output distinguishes admitted evidence from rejected or repaired alternatives.
- Public machine-readable explanation includes `schema_version` and `projection_kind`.
- Tests fail if explanation output drops source lineage or invariant references.
- The explanation path does not call LLMs or provider tools.

## Review Trigger

Revisit this ADR if explanation output becomes large enough to require compact and full modes.

