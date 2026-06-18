# ADR-0019: Document Adapter Contradiction Fixtures Protect Boundary Purity

## Status

Accepted

## Context

Document adapters such as Docling can expose valuable layout, table, OCR, and structural evidence. They can also smuggle provider assumptions into the system if their output is accepted without contradiction tests.

Catalyst admits adapters at the boundary. Internal formation must receive Catalyst-native evidence and must not treat provider structure as source truth.

## Decision

Catalyst will add document adapter contradiction fixtures.

These fixtures should prove that adapter-derived evidence remains boundary evidence, that source spans remain reversible, and that false or ambiguous document structure does not silently become admitted chunks.

## Evidence

- ADR-0008 admits Docling as a boundary adapter only.
- Boundary purity governance prevents concrete adapters from being imported inward.
- Existing contradiction tests already protect false Markdown and source-lineage behavior.

## Alternatives Considered

- Trust document adapter structure as authoritative: rejected because adapter output is evidence, not truth.
- Test only happy-path document parsing: rejected because boundary failures usually appear in ambiguous documents.
- Move document parsing logic inward: rejected because it violates boundary purity.

## Consequences

Document adapter tests should include adversarial or ambiguous document shapes.

Fixtures should not require optional provider dependencies unless isolated in optional/contract test paths.

Adapter evidence must preserve source identity and reversible spans.

## Implementation Acceptance Criteria

- Tests cover table continuation, OCR hyphenation/noise, layout order ambiguity, and false headings where practical.
- Adapter-derived observations preserve Catalyst source IDs and reversible offsets.
- False structure remains rejected, repaired, or explicitly inspectable.
- Optional adapter dependencies remain optional.
- Boundary purity checks continue to reject inward imports from concrete adapters.

## Review Trigger

Revisit this ADR if a document adapter becomes central enough to require a stronger public adapter contract or separate fixture package.

