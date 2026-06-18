# ADR-0014: Retrieval Ingestion Examples Stay Boundary-External

## Status

Accepted

## Context

Catalyst is intended to be used inside other software, including retrieval systems, agentic context processors, and document curation tools. Those consumers need examples for mapping Catalyst output into ingestion records.

The core package should not become shaped around a single downstream application, vector database, or provider DTO.

## Decision

Catalyst will provide app-neutral retrieval ingestion examples while keeping app-specific mappings outside the core model.

The authoritative Catalyst outputs remain chunk graphs and public projections. Example ingestion records may show how to carry chunk ID, source ID, text, spans, schema version, metadata, and relation references into a consumer system.

Vector database names, Crux Studio-specific names, Neuroca-specific names, and provider-specific DTOs do not belong in Catalyst core types.

## Evidence

- Public projections are already versioned contracts.
- Boundary ports already keep adapters outside internal formation and invariant logic.
- Downstream applications need stable examples, but their storage and ranking choices are not Catalyst admission rules.

## Alternatives Considered

- Add a first-class vector database ingestion model to core: rejected because it would couple Catalyst to one storage shape.
- Provide no ingestion examples: rejected because consumers need clear mapping guidance.
- Add app-specific DTOs for each consumer: rejected because this would turn Catalyst into an application integration layer.

## Consequences

Examples and tests may validate projection field availability without adding runtime dependencies.

Application adapters should live outside Catalyst unless they are admitted as generic boundary adapters.

Provider-token and vector-store mappings remain downstream responsibilities unless a later ADR admits a generic port.

## Implementation Acceptance Criteria

- Documentation includes a generic retrieval ingestion example.
- Example records include chunk ID, source ID, indexed text, spans, projection schema version, and relation references where available.
- Tests fail if required public projection fields used by the example drift.
- No vector database dependency is added to required runtime dependencies.
- No downstream application name becomes a core Catalyst type.

## Review Trigger

Revisit this ADR if multiple independent consumers require the same ingestion contract and it becomes worth admitting a generic boundary port.

