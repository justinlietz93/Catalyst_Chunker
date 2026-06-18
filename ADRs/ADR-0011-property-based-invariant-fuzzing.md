# ADR-0011: Property-Based Invariant Fuzzing

## Status

Accepted

## Context

Catalyst already has unit, integration, contradiction, contract, and fixture-based tests. Those tests prove named cases, but they cannot cover the full surface where source spans, Unicode, whitespace, atomic runs, and fallback repair interact.

The most important Catalyst guarantees are invariant-shaped: source coverage, source lineage, offset reversibility, token-budget honesty, rejection visibility, and stable identity. Those guarantees should be tested across generated source forms, not only curated examples.

## Decision

Catalyst will add property-based invariant fuzzing as a development and CI test layer.

Generated inputs are test evidence. They do not create new runtime truth, and they do not relax any invariant. When a generated case exposes a bug, the minimized failing input should become a named regression fixture where practical.

Property-based testing remains a development dependency only.

## Evidence

- Offset reversibility and source lineage are sensitive to character, byte, and span boundaries.
- Token-budget behavior is sensitive to whitespace, punctuation, and long atomic runs.
- Stable IDs must remain deterministic across repeated calls and equivalent structured inputs.
- Existing curated fixtures already show the value of source-family-specific contradiction tests.

## Alternatives Considered

- Keep only curated fixtures: rejected because curated fixtures miss combinatorial span and Unicode cases.
- Add unbounded random tests: rejected because unreproducible failures would weaken CI.
- Treat provider-token fuzzing as core: rejected because provider tokenization belongs at a boundary adapter unless admitted as active budget evidence.

## Consequences

The development dependency set may include a property-based testing library.

Generated tests must be bounded enough to run in CI without making the suite flaky.

Failures should produce durable regression cases instead of remaining anonymous generated inputs.

## Implementation Acceptance Criteria

- Property tests cover stable ID determinism.
- Property tests cover offset reversibility for admitted chunks across ASCII and Unicode inputs.
- Property tests cover source coverage and lineage for generated chunkable inputs.
- Property tests cover token-budget behavior for whitespace-delimited text and document long atomic-token behavior explicitly.
- Any flaky generated strategy is bounded, seeded, or moved out of required CI.

## Review Trigger

Revisit this ADR if property tests become flaky, too slow for CI, or start encoding assumptions that contradict Catalyst's invariant definitions.

