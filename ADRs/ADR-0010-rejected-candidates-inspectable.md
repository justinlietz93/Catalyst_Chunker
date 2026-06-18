# ADR-0010: Rejected Candidates Remain Inspectable

## Status

Accepted

## Context

Candidate rejection is part of Catalyst's truth machinery. If failed candidates disappear, the system cannot explain why a chunk graph was admitted, why another structure failed, whether a boundary was uncertain, or whether repair hid a contradiction.

The standards file defines rejection visibility as a required invariant and names rejection records, repair records, decision records, audit projections, and boundary inspection projections as core architecture.

## Decision

Rejected candidates remain inspectable.

Every rejected candidate or candidate set must produce a rejection record containing:

- candidate identity
- rejection reason
- supporting evidence or failed invariant
- relevant source spans
- repair attempt, if any
- reconsideration trigger where appropriate

Audit and boundary inspection projections must be able to expose rejected candidates without presenting them as accepted structure.

## Evidence

- `ARCHITECTURE_STANDARDS.md` requires I011 Rejection Visibility and says rejected candidates must produce rejection records.
- `EMERGENCE_BASED_ARCHITECTURE.md` lists invisible rejection as an anti-pattern and requires rejected or uncertain structures to remain inspectable.
- The research report supports comparing candidate strategies and evaluating boundary clarity rather than accepting one hidden splitter output.

## Alternatives Considered

- Drop failed candidates after selection: rejected because it destroys auditability.
- Keep only aggregate rejection counts: rejected because counts cannot explain source-local contradictions.
- Log rejections only in debug mode: rejected because rejection visibility is an invariant, not a debugging convenience.

## Consequences

Formation and selection code must emit rejection records as normal outputs.

Audit projections need stable schema space for rejected candidates, repairs, warnings, and violations.

Storage and export formats must account for negative evidence, not only admitted chunks.

## Review Trigger

Revisit this ADR if rejection records become too large for a given operating mode and Catalyst needs a documented compaction policy that preserves audit truth without retaining every full candidate body.
