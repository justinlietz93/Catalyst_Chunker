# Catalyst Invariants

Invariants are admission gates and audit facts. They do not create chunks; they verify whether admitted or candidate structure remains lawful.

| ID | Check | Location | Purpose |
|---|---|---|---|
| `I001` | source coverage | `invariant/checks/source_coverage_check.py` | Required spans are covered by admitted chunks or candidates. |
| `I002` | source lineage | `invariant/checks/source_lineage_check.py` | Every admitted item retains source ID and spans. |
| `I003` | offset reversibility | `invariant/checks/offset_reversibility_check.py` | Character offsets map back to canonical UTF-8 byte offsets. |
| `I006` | fallback evidence | `invariant/checks/fallback_evidence_check.py` | Recursive or fallback strategies declare why fallback was needed. |
| `I007` | token budget honesty | `invariant/checks/token_budget_check.py` | Accepted items do not exceed hard token budgets silently. |
| `I010` | projection schema | `invariant/checks/projection_schema_check.py` | Public records declare `schema_version` and `projection_kind`. |
| `I011` | rejection visibility | `invariant/checks/rejection_visibility_check.py` | Rejected candidates remain inspectable. |

## Enforcement Points

- `chunk_source` runs coverage, lineage, offset, token, fallback, and rejection checks.
- `chunk_parsed_code` runs coverage, lineage, offset, token, and rejection checks.
- CLI output is schema checked before writing or printing.
- Retrieval sanity reports include hard invariant outcomes but are diagnostic only.

## Violation Behavior

If an admission invariant fails, operations raise `InvariantViolation`. Candidate-evaluation and retrieval-sanity reports expose failures as data and do not override invariant authority with quality scores.
