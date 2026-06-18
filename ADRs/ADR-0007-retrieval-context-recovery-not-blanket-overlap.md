# ADR-0007: Retrieval Uses Parent/Child And Sentence-Window Recovery Instead Of Blanket Overlap

## Status

Accepted

## Context

Overlap is often used to compensate for broken chunk boundaries, but blanket overlap duplicates material, inflates indexes, and can hide whether context was actually earned by source evidence. Catalyst needs retrieval context without letting overlap become a substitute for admitted structure.

The standards file says Catalyst should prefer precise chunks plus parent/child recovery, sentence-window projection, and dependency-specific context.

## Decision

Catalyst retrieval uses parent/child and sentence-window recovery instead of blanket overlap.

The default retrieval shape is:

```text
precise admitted chunks
  + parent/child context recovery
  + sentence-window context recovery
  + explicit dependency-specific context where evidence supports it
```

Overlap is allowed only when earned by evidence such as pronoun dependency, definition dependency, citation dependency, table continuation, speaker-turn continuation, code import dependency, or claim/example dependency.

## Evidence

- `ARCHITECTURE_STANDARDS.md` states that Catalyst should not use dumb overlap as the default.
- The research report recommends precise chunks plus sentence-window or parent/child recovery over always-on overlap.
- EBA projection rules require public views to disclose what was simplified or omitted, which fits explicit context recovery better than hidden duplicate windows.

## Alternatives Considered

- Fixed overlap on every chunk: rejected because it is not evidence-specific and increases duplication.
- No context recovery: rejected because precise retrieval chunks often need surrounding context for answer assembly.
- One large chunk size: rejected because large chunks trade away retrieval precision and can bury relevant spans.

## Consequences

Formation must preserve chunk relations that projections can use for parent, child, previous, next, continuation, and dependency recovery.

Retrieval projection must distinguish indexed text from recovered context.

Benchmark fixtures should track index cost, retrieval quality, and answer-context adequacy without assuming overlap is free.

## Implementation Acceptance Criteria

- Retrieval projections distinguish indexed chunk text from recovered context.
- Chunk graphs preserve relations needed for parent, child, previous, next, continuation, and dependency recovery.
- Fixed overlap is not a default setting.
- Any overlap-like duplication cites evidence for the dependency it preserves.

## Review Trigger

Revisit this ADR if benchmark fixtures show a source family where fixed overlap consistently outperforms relation-based recovery while preserving source lineage, audit clarity, and acceptable index cost.
