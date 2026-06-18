# ADR-0006: Semantic Chunking Is A Refinement Strategy, Not The Primary Strategy

## Status

Accepted

## Context

Semantic chunking can detect topic shifts where document structure is weak, but it can also import model behavior before source evidence and invariants have done their work. Catalyst should use semantic signals as observations or refinements, not as the first authority over chunk formation.

The standards file places semantic refinement after source-native structure, paragraph/header grouping, AST boundaries, recursive fallback, and dynamic token sizing.

## Decision

Semantic chunking is admitted as a refinement strategy.

It may:

- propose boundary observations
- refine weak structural regions
- help score semantic discontinuity
- support specialized candidate sets when policy permits

It may not:

- replace source lineage
- define Catalyst's primary prose strategy
- override hard invariants
- silently erase or merge source material
- become mandatory for baseline CPU-first operation

## Evidence

- `ARCHITECTURE_STANDARDS.md` lists `SemanticShiftObservation` and `SemanticRefinementCandidateSet`, but makes structure-first grouping the prose default.
- The research report recommends a small local semantic pass only where simple structural grouping is insufficient.
- EBA separates observation from decision; semantic model output can be evidence, but admission still belongs to invariant-governed formation.

## Alternatives Considered

- Embedding-first chunk formation: rejected because it risks making model similarity the source of truth.
- LLM-guided chunking as default: rejected because the report treats it as costly and specialized for constrained local systems.
- No semantic refinement: rejected because weak-structure documents may need local semantic evidence to resolve ambiguous boundaries.

## Consequences

Semantic instruments must be optional, policy-controlled, and auditable.

Candidate records must distinguish semantic evidence from structural evidence.

The system must still operate correctly without embeddings or LLM calls in the baseline path.

## Review Trigger

Revisit this ADR if Catalyst gains a source family or operating mode where semantic refinement is required for invariant-preserving admission and the cost, reproducibility, and boundary-purity burdens are explicitly handled.
