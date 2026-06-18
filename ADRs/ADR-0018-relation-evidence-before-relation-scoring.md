# ADR-0018: Relation Evidence Comes Before Relation Scoring

## Status

Accepted

## Context

Chunk relations are useful for retrieval context recovery. Catalyst already records relation kinds such as previous sibling, dependency, definition, citation support, and code calls.

Downstream systems may want scores or confidence values on relations, but scores can become misleading if the relation does not first cite the evidence that earned it.

## Decision

Catalyst will refine relation evidence before adding relation scoring.

Relation records should make the source-local reason for a relation inspectable. Any future score must remain diagnostic and cannot substitute for evidence IDs, source spans, or relation kind.

## Evidence

- ADR-0007 prefers relation-based context recovery over blanket overlap.
- Current relation records already have `evidence_ids`.
- Germinal structure should expose how a relation formed before ranking it.

## Alternatives Considered

- Add confidence scores immediately: rejected because scores without evidence can look authoritative.
- Keep relations as unexamined graph edges: rejected because downstream context recovery needs explainable edges.
- Replace relation kinds with numeric weights: rejected because this destroys semantic inspectability.

## Consequences

Formation code that creates non-adjacent relations should cite evidence when available.

Tests should check evidence coverage for dependency-like relation kinds.

Relation scoring, if later admitted, requires a separate ADR or an update to this one.

## Implementation Acceptance Criteria

- Dependency-like relation records include evidence IDs where source evidence exists.
- Relation projections expose relation kind and evidence references.
- Tests distinguish adjacency relations from evidence-bearing semantic/dependency relations.
- No score field is required for relation admission.
- Any future relation score is documented as diagnostic, not admission authority.

## Review Trigger

Revisit this ADR if multiple downstream consumers require relation scores and Catalyst has enough evidence-bearing relation fixtures to score without hiding formation reasons.

