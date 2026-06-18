# Stable IDs

Catalyst uses deterministic IDs for sources, observations, candidates, chunks, decisions, repairs, projections, and other traceable records.

## Current Algorithm

The current algorithm is `catalyst.stable_id.v1`.

Implementation facts:

- Hash algorithm: `sha256`
- Part separator before hashing: ASCII unit separator, represented as `\x1f`
- Default digest size in IDs: first 16 hex characters
- Format: `<prefix>_<digest>`

The helper `stable_id_metadata()` exposes these facts to callers that need diagnostics or migration records.

## Inputs

Each call site chooses the stable parts that define identity for that record. Typical inputs include source ID, source kind, content hashes, spans, policy IDs, evidence IDs, and candidate IDs.

Changing the call-site parts changes the resulting ID even if the hash algorithm does not change.

## Compatibility

Changing the hash algorithm, separator, default digest size, or meaning of call-site inputs requires an explicit release note. A future incompatible algorithm should use a new algorithm version.

Stable IDs are deterministic identifiers, not security boundaries.
