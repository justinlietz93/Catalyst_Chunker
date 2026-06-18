# Catalyst Projections

Projections are versioned public views over admitted or inspectable Catalyst records. They do not create source truth or silently rewrite accepted chunks.

## Current Schemas

| Projection | Version |
|---|---|
| retrieval | `catalyst.retrieval.v1` |
| audit | `catalyst.audit.v1` |
| boundary inspection | `catalyst.boundaries.v1` |
| candidate evaluation | `catalyst.candidate_evaluation.v1` |
| parent/child | `catalyst.parent_child.v1` |
| sentence window | `catalyst.sentence_window.v1` |
| code | `catalyst.code.v1` |
| retrieval sanity | `catalyst.retrieval_sanity.v1` |
| performance benchmark | `catalyst.performance_benchmark.v1` |
| context recovery benchmark | `catalyst.context_recovery_benchmark.v1` |
| specialized mode admission | `catalyst.specialized_mode_admission.v1` |

Every public projection must include `schema_version` and `projection_kind`.

## Lossless And Lossy Views

Retrieval records preserve chunk text, source spans, warnings, and relations needed for retrieval. Audit and boundary-inspection records preserve rejected candidates, repairs, violations, warnings, and evidence summaries. Sentence-window and parent/child projections add context views without rewriting accepted chunk identity.

If a projection omits internal detail, it must expose that through `warnings`, `omissions`, audit records, or a narrower projection kind.

## Retrieval Sanity

Retrieval sanity records compare candidate strategies against held-out fixture evidence. Each strategy result includes hard invariant status, answer-context adequacy, cost, and `retrieval_metrics`.

The default ranking method is `lexical_query_overlap.v1`. It reports ranked candidate IDs, relevant candidate IDs, `recall_at_1`, `recall_at_3`, and `mrr`. These fields are diagnostic and cannot admit chunks that fail hard invariants.

## Performance Benchmark

Performance benchmark records compare fixture-defined source shapes against chunking strategies. Each strategy result includes source measures, elapsed time, `tracemalloc` peak memory, chunk count, token total, repair count, strategy identity, and invariant summary.

Timing and memory fields are diagnostic, machine-dependent evidence. They are not admission gates and cannot override hard invariants.

## Compatibility

Schema versions are append-only within a version. Removing fields or changing meaning requires a new schema version. Tests should fail any unversioned public projection.

## Deprecation

Deprecated projections must remain readable until a replacement is implemented, documented, and covered by contract tests.
