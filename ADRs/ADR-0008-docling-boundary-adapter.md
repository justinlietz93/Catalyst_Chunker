# ADR-0008: Docling Is Admitted As A Boundary Adapter, Not As An Internal Model

## Status

Accepted

## Context

Docling is useful for documents and PDFs because it can expose structural elements, metadata, tables, and local conversion artifacts. That usefulness does not make Docling's object model Catalyst's internal model.

Catalyst's architecture requires external tools to remain boundary mechanisms or observation instruments. Boundary tools may reveal evidence, but they cannot define internal truth.

## Decision

Docling is admitted as a boundary adapter.

The Docling adapter may:

- load or convert supported document sources
- expose source-native elements and metadata as observations
- preserve offsets, element IDs, table structure, page information, and conversion traces where available
- support PDF/document source families

The Docling adapter may not:

- define `SourceRecord`, `SourceSpan`, `Observation`, `ChunkCandidate`, or `ChunkGraph`
- bypass Catalyst invariants
- decide accepted chunk structures by provider authority alone
- leak Docling-specific models into internal layers

## Evidence

- `ARCHITECTURE_STANDARDS.md` names Docling as a boundary adapter and says external tools cannot define Catalyst's internal truth.
- The research report recommends Docling as a strong local document/PDF front end for CLI systems, especially where structure recovery matters.
- `EMERGENCE_BASED_ARCHITECTURE.md` states that frameworks, storage, APIs, and tools are boundary mechanisms.

## Alternatives Considered

- Make Docling the internal document model: rejected because provider assumptions would become native Catalyst concepts.
- Avoid Docling entirely: rejected because its structural observations are useful for PDFs and richly structured documents.
- Treat Docling chunks as accepted Catalyst chunks: rejected because accepted chunks must pass Catalyst evidence, invariant, selection, and projection rules.

## Consequences

Catalyst needs explicit boundary ports for document parsing and source loading.

Docling adapter contract tests must prove translation into Catalyst-native records without inward leakage of concrete adapter types.

Alternative adapters such as Unstructured, Haystack, LlamaIndex, Tree-sitter, or ast-grep can be admitted under the same boundary-purity rule.

## Review Trigger

Revisit this ADR if Docling becomes unavailable, its output semantics change materially, or Catalyst admits a different document adapter as the preferred document/PDF boundary.
