# Decision Ledger

This ledger tracks the implementation status of accepted architecture decisions.

| ADR | Decision | Status | Implementation Status |
|---|---|---|---|
| ADR-0001 | Catalyst uses EBA layer admission, not service/repository architecture. | Accepted | Baseline implemented |
| ADR-0002 | Source lineage is mandatory for every accepted chunk. | Accepted | Baseline implemented |
| ADR-0003 | Fixed-size slicing is fallback only, never default. | Accepted | Recursive fallback implemented; fixed-size slicing still unavailable |
| ADR-0004 | Structure-first paragraph/header grouping is the default prose strategy. | Accepted | Baseline implemented |
| ADR-0005 | Code chunking requires AST-aware observation by default. | Accepted | Implemented with Python AST baseline, optional ast-grep boundary adapter, and AST repair/rejection path |
| ADR-0006 | Semantic chunking is a refinement strategy, not the primary strategy. | Accepted | Implemented as optional evidence-only semantic observation, embedding adapter, refinement candidate set, and audit distinction |
| ADR-0007 | Retrieval uses parent/child and sentence-window recovery instead of blanket overlap. | Accepted | Context projections and retrieval sanity fixtures implemented; relation-recovery benchmarks pending |
| ADR-0008 | Docling is admitted as a boundary adapter, not as an internal model. | Accepted | Boundary adapter implemented with optional dependency |
| ADR-0009 | Public projections require schema versions. | Accepted | Baseline implemented |
| ADR-0010 | Rejected candidates remain inspectable. | Accepted | Baseline implemented |
| ADR-0011 | Property-based invariant fuzzing is admitted as a development test layer. | Accepted | Implemented in 0.1.5 |
| ADR-0012 | Retrieval evaluation uses held-out query metrics as diagnostic evidence. | Accepted | Implemented in 0.1.6 |
| ADR-0013 | Performance benchmarks are diagnostic evidence, not admission invariants. | Accepted | Implemented in 0.1.7 |
| ADR-0014 | Retrieval ingestion examples stay app-neutral and boundary-external. | Accepted | Implemented in 0.1.8 |
| ADR-0015 | Telemetry adapters are optional boundary adapters. | Accepted | Implemented in 0.1.8 |
| ADR-0016 | Messy source families require contradiction fixtures. | Accepted | Planned |
| ADR-0017 | Admission explanation traces evidence to decision. | Accepted | Planned |
| ADR-0018 | Relation evidence comes before relation scoring. | Accepted | Planned |
| ADR-0019 | Document adapter contradiction fixtures protect boundary purity. | Accepted | Planned |
