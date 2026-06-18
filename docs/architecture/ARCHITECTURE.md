# Catalyst Architecture

Catalyst is organized around evidence, boundaries, and admission. External tools may observe source material, but accepted chunks are admitted only after Catalyst-native formation and invariants.

## Layer Map

The implemented package follows this direction:

- `source`: immutable source identity, spans, lineage, and normalization.
- `observation`: evidence records and instruments that observe source without admitting chunks.
- `invariant`: checks that block or report invalid admission.
- `formation`: candidate boundaries, candidate sets, repairs, rejection records, and selection.
- `projection`: accepted chunk graphs and versioned public views.
- `operation`: explicit use cases that combine source, evidence, formation, invariants, and projections.
- `boundary`: ports, concrete adapters, and CLI presentation.
- `policy`: explicit admission rules for adapters, overlap, and specialized modes.
- `shared`: errors and stable identifiers.

Concrete boundary adapters do not flow inward. Internal layers use Catalyst-native records such as `SourceRecord`, `EvidenceSet`, `ChunkCandidateSet`, and `ChunkGraph`.

## Default Flow

1. Source bytes become a `SourceRecord`.
2. Instruments produce observations in an `EvidenceSet`.
3. Formation strategies propose `ChunkCandidateSet` records.
4. The selector admits one candidate set and keeps rejection records inspectable.
5. Invariants verify coverage, lineage, offset reversibility, token budget honesty, fallback evidence, rejection visibility, and projection versioning.
6. Accepted chunks become a `ChunkGraph`.
7. Public projections render versioned retrieval, audit, boundary, code, parent/child, sentence-window, candidate-evaluation, and retrieval-sanity records.

## Strategy Order

The baseline path remains structure first:

- prose: paragraph grouping, recursive fallback only after structural failure
- document structure: Docling or other adapters as boundary evidence
- code: AST observations and AST-backed candidate formation
- context recovery: parent/child and sentence-window projections
- semantic refinement: optional evidence-only refinement after structural candidates
- specialized modes: late chunking, LLM assistance, and chunk-free retrieval are gated modes, not defaults

## Enforcement

Architecture is enforced by:

- `.importlinter`
- `governance/tools/enforce_file_size.py`
- `governance/tools/enforce_native_names.py`
- `governance/tools/enforce_boundary_purity.py`
- unit, contract, contradiction, integration, and e2e tests
