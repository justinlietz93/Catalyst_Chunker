# ADR-0009: Public Projections Require Schema Versions

## Status

Accepted

## Context

Catalyst exposes internal results through projections for retrieval, audit, boundary inspection, summaries, code views, and exports. These public views are contracts. Without schema versions, downstream users cannot distinguish stable output from experimental or changed output.

Projection must render admitted structures without redefining internal truth.

## Decision

Every public Catalyst projection must include:

- `schema_version`
- `projection_kind`
- source lineage where applicable
- warnings where applicable
- omissions where applicable
- an error envelope for failure cases

Breaking public projection changes require a schema version bump, documentation update, test update, and ADR or decision ledger entry.

## Evidence

- `ARCHITECTURE_STANDARDS.md` defines projection versioning as invariant I010.
- The governance section requires no public projection without `schema_version`.
- `EMERGENCE_BASED_ARCHITECTURE.md` states that projection must be versioned when public and must not lie about simplification or omission.

## Alternatives Considered

- Unversioned JSON/JSONL exports: rejected because machine consumers need compatibility guarantees.
- Version only API responses: rejected because CLI exports, reports, and index artifacts are also public contracts.
- Version by filename only: rejected because artifacts can be copied, concatenated, or transported without filename context.

## Consequences

Projection schemas must be treated as first-class artifacts with contract tests.

Public projection writers must fail or warn if `schema_version` or `projection_kind` is absent.

Schema evolution must be deliberate rather than accidental.

## Review Trigger

Revisit this ADR if Catalyst introduces a private, explicitly unstable diagnostic output class that is not public, not machine-contractual, and clearly marked as non-contract output.
