# ADR-0001: Catalyst Uses EBA Layer Admission, Not Service/Repository Architecture

## Status

Accepted

## Context

Catalyst is not a CRUD application and should not begin from generic application roles such as controllers, services, repositories, workers, or pipelines. Its central burden is lawful chunk formation from source material: preserve what was received, observe structure, test invariants, form candidates, admit or reject structures, and project external views.

The local architecture standards define Catalyst as an invariant-first chunk formation engine. The local EBA document defines the architectural admission order as source, observation, invariant, formation, operation, projection, and boundary.

## Decision

Catalyst admits internal structure through EBA layer order:

```text
source
  -> observation
  -> invariant
  -> formation
  -> operation
  -> projection
  -> boundary
```

Catalyst will not use service/repository architecture as its native organizing model. Terms such as `Service`, `Repository`, `Controller`, `Processor`, `Manager`, `Worker`, and `Pipeline` require a later ADR if they are introduced as internal architecture nouns.

## Evidence

- `ARCHITECTURE_STANDARDS.md` defines Catalyst as source-preserving, observation-driven, invariant-checked, multi-candidate, projection-plural, and boundary-pure.
- `EMERGENCE_BASED_ARCHITECTURE.md` states that EBA begins with material received, observations, invariants, and evidence-backed formation rather than framework conventions.
- The research report frames chunking as structure formation from source material, not as fixed pipeline execution.

## Alternatives Considered

- Service/repository architecture: rejected because it imports application vocabulary before Catalyst has admitted native chunking structures.
- Splitter pipeline architecture: rejected because it makes chunking look like sequential text processing rather than evidence-backed candidate admission.
- Framework-first CLI/API layout: rejected because boundary presentation would define internal concepts too early.

## Consequences

Catalyst's codebase will be organized around native concepts such as `SourceRecord`, `Observation`, `Invariant`, `ChunkCandidate`, `ChunkGraph`, `Projection`, and `DecisionLedger`.

This makes architecture reviews stricter: new internal nouns need an admission path, and generic names must be justified.

Boundary code can still use framework conventions externally, but those conventions cannot define internal truth.

## Implementation Acceptance Criteria

- Source, observation, invariant, formation, operation, projection, boundary, policy, and shared layers exist as first-class package areas.
- Concrete boundary adapters and presentation code are not imported by internal layers.
- Generic architecture names such as service, repository, controller, manager, processor, worker, and pipeline are rejected by governance unless admitted by ADR.
- At least one runnable path follows source -> observation -> invariant -> formation -> operation -> projection -> boundary.

## Review Trigger

Revisit this ADR only if Catalyst develops a stable internal responsibility that cannot be named precisely within the EBA vocabulary and can be proved narrower than a generic service/repository role.
