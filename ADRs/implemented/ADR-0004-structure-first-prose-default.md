# ADR-0004: Structure-First Paragraph/Header Grouping Is The Default Prose Strategy

## Status

Accepted

## Context

Prose usually exposes structure through headings, paragraphs, lists, sections, tables, citations, and local adjacency before any embedding or token heuristic is needed. Catalyst's formation layer should therefore begin from observed prose structure and only refine when required by invariants or policy.

The research report identifies paragraph/header-first and structure-aware strategies as the strongest practical center for constrained CLI systems.

## Decision

For prose sources, Catalyst's default formation strategy is structure-first paragraph/header grouping.

The default prose candidate path is:

```text
source spans
  -> heading, paragraph, list, sentence, table, and token observations
  -> invariant checks
  -> paragraph/header candidate groups
  -> recursive or dynamic-token repair where needed
  -> admitted chunk graph
```

Semantic refinement may operate only after this structural candidate exists and only when evidence shows weak or ambiguous boundaries.

## Evidence

- `ARCHITECTURE_STANDARDS.md` lists Markdown, plain text, legal docs, scientific papers, long books, and weak-structure docs with structure-first primary strategies.
- The local research report recommends structure-aware grouping plus token-aware normalization and optional semantic refinement.
- EBA requires observation before decision, which matches paragraph/header evidence before chunk admission.

## Alternatives Considered

- Semantic-first prose chunking: rejected because embeddings can suggest boundaries but should not replace observed document structure.
- Token-first prose chunking: rejected because token counts refine budget compliance rather than source meaning.
- LLM-guided prose segmentation as default: rejected because it is too expensive and too boundary-authoritative for the baseline constrained CLI design.

## Consequences

Paragraph, heading, list, table, sentence, and tokenizer instruments become early MVP work.

Candidate selection must score structural boundary clarity, orphan count, repair count, size variance, and token budget compliance.

Documents with weak structure can still use semantic refinement, but that refinement remains subordinate to lineage and invariant records.

## Implementation Acceptance Criteria

- Prose formation uses heading, paragraph, list, sentence, and token observations before fallback.
- Very short adjacent prose regions can merge into one candidate when policy permits.
- Oversized prose regions are repaired or rejected before admission.
- Semantic refinement cannot run until a structural candidate exists.

## Review Trigger

Revisit this ADR if a source family lacks stable prose markers and repeatedly produces better admitted chunk graphs through another strategy without violating lineage, coverage, or projection invariants.
