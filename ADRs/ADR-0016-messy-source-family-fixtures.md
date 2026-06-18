# ADR-0016: Messy Source Families Require Contradiction Fixtures

## Status

Accepted

## Context

Catalyst is useful only if source structure can remain inspectable under imperfect source conditions. Real source material may include OCR noise, multi-column extraction order problems, malformed Markdown, mixed tables, and unusual code shapes.

Adding new parser authority would weaken the architecture. The better next step is to test whether Catalyst preserves lineage, rejection visibility, and invariant behavior when source evidence is messy or partially misleading.

## Decision

Catalyst will add messy source-family contradiction fixtures.

These fixtures are proof obligations, not new formation authority. They should expose cases where source evidence is ambiguous, noisy, incomplete, or provider-shaped, and they should prove that Catalyst either admits lawful chunks or produces inspectable rejection/repair evidence.

## Evidence

- Existing contradiction fixtures already protect source lineage and false-structure cases.
- ADR-0008 admits document parsers only as boundary adapters.
- Germinal formation requires source-local evidence to remain inspectable before structure is admitted.

## Alternatives Considered

- Add provider-specific parser trust rules: rejected because parser output is evidence, not authority.
- Ignore messy source families until users report failures: rejected because these cases are predictable and high-impact.
- Treat all messy extraction as plain text: rejected because that hides source-family contradictions instead of testing them.

## Consequences

Test fixtures should cover noisy source families without adding runtime dependencies.

New fixtures should identify the contradiction being tested and the expected invariant behavior.

When a fixture reveals an adapter problem, the repair must preserve boundary purity.

## Implementation Acceptance Criteria

- Fixtures cover OCR noise, multi-column extraction, tables, malformed Markdown, and unusual code shape.
- Each fixture declares the source-family risk it tests.
- Tests prove either lawful admission or inspectable rejection/repair evidence.
- No fixture requires a provider dependency in the default test path.
- No parser output is accepted as chunk truth without Catalyst-native spans and invariants.

## Review Trigger

Revisit this ADR if messy source fixtures become large enough to require a separate slow or optional test group.

