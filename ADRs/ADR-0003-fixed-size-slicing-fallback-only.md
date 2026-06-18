# ADR-0003: Fixed-Size Slicing Is Fallback Only, Never Default

## Status

Accepted

## Context

Fixed-size slicing imposes an external window before the source has revealed its native structure. It can cut across paragraphs, headings, tables, code syntax, legal clauses, or definitions while appearing mechanically regular.

The local research report states that fixed character chunking trails structure-preserving and adaptive methods. The standards file therefore places source-native structure, paragraph/header grouping, AST boundaries, recursive fallback, and dynamic token sizing ahead of any crude slicing behavior.

## Decision

Fixed-size slicing is admitted only as an explicit fallback strategy after source-native, structural, recursive, token-aware, and source-family-specific options have failed or are unavailable.

Fixed-size fallback must:

- preserve source lineage
- declare itself in the decision record
- satisfy token budget and projection invariants
- leave rejection or repair records for better candidates that failed
- never become Catalyst's default prose, code, PDF, or retrieval strategy

## Evidence

- `ARCHITECTURE_STANDARDS.md` states that Catalyst does not split text; it admits chunk structures from source evidence.
- The default strategy matrix ranks source-native structure, paragraph/header grouping, AST boundaries, recursive fallback, and dynamic token sizing before late or specialized methods.
- The research report recommends structure-aware chunking first and says fixed-size character slicing is not supported as the default by current evidence.

## Alternatives Considered

- Fixed token windows as default: rejected because token limits may refine structure but cannot define it first.
- Fixed character windows as default: rejected because character count has no source-native boundary authority.
- Always-on overlap over fixed windows: rejected because overlap masks broken boundaries and increases index cost without proving structure.

## Consequences

Catalyst must implement structural candidates before relying on fixed-size fallback.

Fallback output must be audit-visible, so downstream users can distinguish admitted source structure from emergency segmentation.

Benchmark fixtures should compare fallback output against structure-first candidates to prevent convenience from replacing evidence.

## Implementation Acceptance Criteria

- The default candidate list tries source-structure candidates before any recursive or fixed-size fallback.
- A fallback candidate set must include a fallback reason record that cites the failed or unavailable structural evidence.
- Fixed-size slicing is unavailable unless fallback evidence exists and the candidate set is marked as fallback.
- Audit output exposes fallback use through decision, rejection, repair, warning, or candidate-set records.

## Review Trigger

Revisit this ADR if a specific source family proves that fixed-size fallback consistently satisfies Catalyst's invariants and outperforms source-native candidate formation under documented constraints.
