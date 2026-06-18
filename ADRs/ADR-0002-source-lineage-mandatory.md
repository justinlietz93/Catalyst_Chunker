# ADR-0002: Source Lineage Is Mandatory For Every Accepted Chunk

## Status

Accepted

## Context

Catalyst's accepted chunks must remain answerable to the source material that produced them. Without mandatory lineage, a chunk can appear valid while hiding loss, normalization drift, boundary-tool assumptions, or projection-only convenience.

The architecture standards define source coverage, source lineage, and reversible normalization as required invariants. The EBA document treats source identity and lineage as the first architectural burden.

## Decision

Every accepted chunk in Catalyst must carry source lineage.

At minimum, an accepted chunk must identify:

- `source_id`
- one or more source spans or source-native element IDs
- the candidate set that produced it
- evidence, policy, or repair records supporting its admission

Any lossy or partial mode must declare omissions explicitly. Silent loss of source material is not allowed.

## Evidence

- `ARCHITECTURE_STANDARDS.md` requires source coverage, source lineage, reversible normalization, candidate evidence, and token budget honesty.
- `EMERGENCE_BASED_ARCHITECTURE.md` states that derived structures must preserve lineage and that irreversible transformation requires explicit lossy mode.
- The research report identifies source offsets, source-native element IDs, reproducibility, and reversible traces as core invariants for a Catalyst-like system.

## Alternatives Considered

- Text-only chunks: rejected because the chunk text alone cannot prove source coverage or explain boundary decisions.
- Best-effort metadata: rejected because lineage must be an invariant, not a convenience field.
- Lineage only in audit mode: rejected because retrieval, summary, code, and audit projections all need a truthful path back to source.

## Consequences

Formation, repair, and projection logic must preserve source references throughout the admitted chunk graph.

Boundary adapters must translate external parser metadata into Catalyst lineage records instead of leaking provider models inward.

Tests must include contradiction cases where plausible chunks are rejected because they lack adequate source mapping.

## Review Trigger

Revisit this ADR if Catalyst introduces a declared lossy mode with explicit user-facing semantics, omission records, and separate projection contracts.
