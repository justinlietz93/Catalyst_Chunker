# Catalyst System Language

This document records the accepted implementation vocabulary. Names should remain source-preserving and evidence-oriented.

## Accepted Nouns

- `SourceRecord`, `SourceIdentity`, `SourceSpan`, `SourceElement`
- `LineageMap`, `OffsetMap`, `NormalizationTrace`
- `Observation`, `EvidenceSet`, `ObservationReport`
- `Invariant`, `InvariantResult`, `InvariantLedger`, `ViolationRecord`
- `BoundaryCandidate`, `BoundaryMap`, `BoundaryScore`
- `ChunkCandidate`, `ChunkCandidateSet`, `CandidateReason`, `CandidateMetrics`
- `SelectionPolicy`, `SelectionResult`, `DecisionRecord`, `RejectionRecord`, `RepairRecord`
- `AcceptedChunk`, `ChunkRelation`, `ChunkGraph`
- `RetrievalProjection`, `AuditProjection`, `BoundaryInspectionProjection`
- `CodeProjection`, `ParentChildProjection`, `SentenceWindowProjection`

## Boundary-Only Terms

These terms may appear in ports, adapters, or presentation, but should not become internal truth models:

- Docling, Unstructured, Haystack, LlamaIndex
- Tree-sitter, ast-grep
- Sentence Transformers, Model2Vec
- filesystem, JSONL, CLI
- LLM provider names

## Projection-Only Terms

These are public views over admitted structure, not formation authority:

- retrieval record
- audit record
- boundary inspection
- parent/child view
- sentence-window view
- code view
- candidate evaluation
- retrieval sanity report

## Rejected Generic Names

The following names are rejected unless a later ADR explicitly admits them:

- service
- repository
- controller
- manager
- processor
- worker
- pipeline

## Specialized Terms

Late chunking, LLM-guided formation, and chunk-free retrieval are specialized or experimental modes. They must remain policy gated and audit-visible.
