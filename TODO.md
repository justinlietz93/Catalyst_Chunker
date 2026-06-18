# TODO: Catalyst Implementation Sequence

This TODO sequences Catalyst from the architecture standards and ADR-0001 through ADR-0010. Work should proceed in order unless a later task exposes a contradiction that requires revisiting an earlier phase.

## Phase 0: Make The Decisions Enforceable

### Task 0.1: Establish the ADR spine as the build contract

- [x] Step 0.1.1: Treat `ADRs/ADR-0001-eba-layer-admission.md` through `ADRs/ADR-0010-rejected-candidates-inspectable.md` as accepted foundational constraints.
- [ ] Step 0.1.2: Add implementation acceptance criteria to each ADR where terms are still broad, especially fallback eligibility, weak structure, public projection scope, and rejection retention.
- [x] Step 0.1.3: Create or update `docs/DECISION_LEDGER.md` with links to the ten accepted ADRs and their current implementation status.

### Task 0.2: Create the project skeleton without importing generic architecture

- [x] Step 0.2.1: Add `pyproject.toml`, `README.md`, `.importlinter`, and `catalyst.toml`.
- [x] Step 0.2.2: Create `src/catalyst/` with `source/`, `observation/`, `invariant/`, `formation/`, `operation/`, `projection/`, `boundary/`, `policy/`, and `shared/`.
- [x] Step 0.2.3: Create `tests/unit/`, `tests/contract/`, `tests/contradiction/`, `tests/integration/`, and `tests/e2e/`.
- [x] Step 0.2.4: Avoid `service`, `repository`, `controller`, `manager`, `processor`, `worker`, and `pipeline` names unless a later ADR admits one.

### Task 0.3: Establish architecture governance gates

- [x] Step 0.3.1: Add import direction enforcement for the EBA layers.
- [x] Step 0.3.2: Add a native-name check that rejects vague architecture names without ADR coverage.
- [x] Step 0.3.3: Add a file-size check enforcing the 500 LOC rule unless an ADR permits an exception.
- [x] Step 0.3.4: Add projection schema checks for `schema_version` and `projection_kind`.
- [x] Step 0.3.5: Add boundary-purity checks that prevent concrete boundary adapters from being imported inward.

## Phase 1: Preserve Source Identity And Lineage

### Task 1.1: Implement source records and spans

- [x] Step 1.1.1: Implement `SourceIdentity`, `SourceRecord`, `SourceSpan`, and `SourceElement`.
- [x] Step 1.1.2: Include stable source IDs, source kind, raw bytes hash, canonical text hash, metadata, and optional normalization trace IDs.
- [x] Step 1.1.3: Include byte, character, page, line, and element references where available.
- [x] Step 1.1.4: Add unit tests proving source identity and span values are immutable and deterministic.

### Task 1.2: Implement lineage and reversible normalization

- [x] Step 1.2.1: Implement `LineageMap`, `OffsetMap`, `Provenance`, `NormalizationPolicy`, `ReversibleNormalizer`, and `NormalizationTrace`.
- [x] Step 1.2.2: Ensure every normalized span maps back to raw source or declares lossy behavior.
- [x] Step 1.2.3: Add tests for reversible normalization, lossy-mode declaration, and offset preservation.

### Task 1.3: Enforce ADR-0002 at the source boundary

- [x] Step 1.3.1: Define the minimum lineage contract required by every later accepted chunk.
- [ ] Step 1.3.2: Add contradiction fixtures for missing source IDs, broken offsets, and lossy normalization without declaration.
- [x] Step 1.3.3: Fail any accepted chunk fixture that cannot point back to source identity and spans.

## Phase 2: Observe Without Deciding

### Task 2.1: Implement core observation primitives

- [x] Step 2.1.1: Implement `Observation`, `EvidenceSet`, `Confidence`, `Conflict`, and `ObservationReport`.
- [x] Step 2.1.2: Require every observation to carry source span references, confidence, weight, instrument name, and payload.
- [x] Step 2.1.3: Add tests proving observations do not mutate source records.

### Task 2.2: Implement MVP observation instruments

- [x] Step 2.2.1: Implement Markdown heading observation.
- [x] Step 2.2.2: Implement paragraph boundary observation.
- [x] Step 2.2.3: Implement sentence boundary observation.
- [x] Step 2.2.4: Implement tokenizer observation with alignment back to source spans.
- [ ] Step 2.2.5: Add contradiction fixtures for fake headings inside code fences and malformed Markdown regions.

### Task 2.3: Prepare observation extension points

- [ ] Step 2.3.1: Define instrument contracts for table, PDF layout, code AST, and semantic shift observation.
- [ ] Step 2.3.2: Keep external tools as instruments or boundary adapters, not internal truth models.
- [ ] Step 2.3.3: Add tests that reject observations with no source reference.

## Phase 3: Enforce Invariants Before Formation

### Task 3.1: Implement invariant primitives

- [x] Step 3.1.1: Implement `Invariant`, `InvariantResult`, `InvariantRegistry`, `InvariantLedger`, and `ViolationRecord`.
- [x] Step 3.1.2: Ensure invariant failures are reportable and deterministic.
- [x] Step 3.1.3: Add unit tests for registry execution and violation recording.

### Task 3.2: Implement required MVP invariants

- [ ] Step 3.2.1: Implement source coverage checks.
- [x] Step 3.2.2: Implement source lineage checks.
- [ ] Step 3.2.3: Implement offset reversibility checks.
- [x] Step 3.2.4: Implement token budget honesty checks.
- [x] Step 3.2.5: Implement projection versioning checks.

### Task 3.3: Connect invariants to ADR constraints

- [x] Step 3.3.1: Enforce ADR-0002 by failing accepted chunks without lineage.
- [ ] Step 3.3.2: Enforce ADR-0003 by failing fixed-size fallback that lacks fallback evidence.
- [x] Step 3.3.3: Enforce ADR-0009 by failing public projections without schema versions.
- [x] Step 3.3.4: Enforce ADR-0010 by failing selected candidate sets that discard rejections silently.

## Phase 4: Form Prose Candidates Before Any Splitter Fallback

### Task 4.1: Implement boundary and candidate primitives

- [x] Step 4.1.1: Implement `BoundaryCandidate`, `BoundaryMap`, and `BoundaryScore`.
- [x] Step 4.1.2: Implement `ChunkCandidate`, `ChunkCandidateSet`, `CandidateReason`, and `CandidateMetrics`.
- [x] Step 4.1.3: Require every candidate to cite observations, policy, repair records, or fallback records.

### Task 4.2: Implement default prose formation from ADR-0004

- [x] Step 4.2.1: Implement `ParagraphGroupCandidateSet`.
- [ ] Step 4.2.2: Group by heading, paragraph, list, sentence, table, and token observations.
- [x] Step 4.2.3: Preserve source lineage for every candidate span.
- [ ] Step 4.2.4: Add fixtures for very short paragraphs that should merge and very long paragraphs that must split safely.

### Task 4.3: Implement recursive and fixed-size fallback constraints from ADR-0003

- [ ] Step 4.3.1: Implement `RecursiveFallbackCandidateSet`.
- [ ] Step 4.3.2: Define the exact evidence that proves structural candidates failed or were unavailable.
- [ ] Step 4.3.3: Permit fixed-size slicing only after fallback evidence is recorded.
- [ ] Step 4.3.4: Emit audit-visible fallback records whenever fixed-size slicing is used.

### Task 4.4: Implement selection, rejection, and repair records

- [x] Step 4.4.1: Implement `SelectionPolicy`, `Selector`, `DecisionRecord`, `RejectionRecord`, and repair records.
- [x] Step 4.4.2: Score candidates against hard gates and soft metrics from the architecture standards.
- [x] Step 4.4.3: Preserve rejected candidate records according to ADR-0010.
- [x] Step 4.4.4: Add tests that prove rejected candidates remain inspectable after selection.

## Phase 5: Admit Chunk Graphs And Project Public Views

### Task 5.1: Implement admitted chunk graph types

- [x] Step 5.1.1: Implement `AcceptedChunk`, `ChunkRelation`, and `ChunkGraph`.
- [x] Step 5.1.2: Include source IDs, source spans, token counts, chunk kind, candidate set ID, evidence IDs, warning IDs, invariant result IDs, and decision record IDs.
- [ ] Step 5.1.3: Add relation kinds for parent, child, previous, next, continuation, dependency, table, citation, code, summary, and retrieval-window relations.

### Task 5.2: Implement retrieval and audit projections from ADR-0009

- [x] Step 5.2.1: Implement `RetrievalProjection` with `schema_version`, `projection_kind`, lineage, warnings, and omissions.
- [x] Step 5.2.2: Implement `AuditProjection` with coverage, accepted candidate set, rejections, repairs, violations, and warnings.
- [x] Step 5.2.3: Add contract tests that fail unversioned public projections.

### Task 5.3: Implement boundary inspection projection from ADR-0010

- [x] Step 5.3.1: Implement `BoundaryInspectionProjection`.
- [x] Step 5.3.2: Expose boundary candidates, acceptance status, score, evidence, penalties, and rejection records.
- [x] Step 5.3.3: Ensure rejected candidates are inspectable without being presented as accepted chunks.

## Phase 6: Add Explicit Operations And CLI Boundary

### Task 6.1: Implement lawful operation commands

- [x] Step 6.1.1: Implement `chunk-source` as an operation over source, observation, invariant, formation, and projection.
- [x] Step 6.1.2: Implement `inspect-boundaries` as an operation over observations, boundary candidates, and inspection projection.
- [ ] Step 6.1.3: Implement `evaluate-candidates` to compare candidate sets without accepting hidden splitter output.
- [ ] Step 6.1.4: Implement `emit-projection` for retrieval, audit, and boundary inspection outputs.

### Task 6.2: Implement boundary ports

- [x] Step 6.2.1: Define `SourceLoader`, `ArtifactWriter`, `TokenizerPort`, `DocumentParserPort`, `AstParserPort`, `EmbeddingPort`, and `TelemetrySink`.
- [x] Step 6.2.2: Keep ports typed in Catalyst-native concepts rather than provider models.
- [ ] Step 6.2.3: Add contract tests for each port.

### Task 6.3: Implement first concrete boundary adapters

- [x] Step 6.3.1: Implement filesystem source loading.
- [x] Step 6.3.2: Implement JSONL artifact writing.
- [ ] Step 6.3.3: Implement tokenizer adapter.
- [ ] Step 6.3.4: Implement CLI presentation for `chunk`, `inspect-boundaries`, `compare-strategies`, `explain-chunk`, and `audit`.
- [x] Step 6.3.5: Add e2e tests for CLI output schema versions and source lineage.

## Phase 7: Add Rich Document Structure Through Boundary Adapters

### Task 7.1: Implement Docling boundary adapter from ADR-0008

- [ ] Step 7.1.1: Implement Docling document parsing behind `DocumentParserPort`.
- [ ] Step 7.1.2: Translate Docling output into Catalyst source records, observations, and evidence sets.
- [ ] Step 7.1.3: Prevent Docling concrete types from entering internal layers.
- [ ] Step 7.1.4: Add contract tests proving Docling is a boundary adapter, not an internal model.

### Task 7.2: Add PDF and document contradiction fixtures

- [ ] Step 7.2.1: Add fixture for repeated page headers that look like headings.
- [ ] Step 7.2.2: Add fixture for a table split across pages.
- [ ] Step 7.2.3: Add fixture for OCR hyphenation artifacts.
- [ ] Step 7.2.4: Verify coverage, table header preservation, rejection records, and projection versioning.

### Task 7.3: Prepare alternative document adapters

- [ ] Step 7.3.1: Define adapter admission criteria for Unstructured, Haystack, and LlamaIndex.
- [ ] Step 7.3.2: Require each adapter to pass the same port contract tests.
- [ ] Step 7.3.3: Keep provider chunks as observations or candidates, never accepted Catalyst chunks by authority alone.

## Phase 8: Add Hierarchical Retrieval Context Recovery

### Task 8.1: Implement parent/child chunk structure

- [ ] Step 8.1.1: Implement hierarchical candidate strategy.
- [ ] Step 8.1.2: Implement `ParentChildProjection`.
- [ ] Step 8.1.3: Preserve parent, child, previous, next, and continuation relations in the chunk graph.

### Task 8.2: Implement sentence-window recovery from ADR-0007

- [ ] Step 8.2.1: Implement `SentenceWindowProjection`.
- [ ] Step 8.2.2: Distinguish indexed chunk text from recovered context.
- [ ] Step 8.2.3: Add tests proving retrieval context recovery does not rewrite accepted chunk identity.

### Task 8.3: Restrict blanket overlap

- [ ] Step 8.3.1: Define evidence types that permit overlap, including pronoun, definition, citation, table continuation, speaker-turn, code import, and claim/example dependency.
- [ ] Step 8.3.2: Reject fixed overlap as a default setting.
- [ ] Step 8.3.3: Add benchmarks tracking index cost and retrieval quality with relation-based context recovery.

## Phase 9: Add Code Chunking With AST Evidence

### Task 9.1: Implement code AST observation from ADR-0005

- [ ] Step 9.1.1: Implement `AstParserPort`.
- [ ] Step 9.1.2: Add Tree-sitter or ast-grep adapter behind the port.
- [ ] Step 9.1.3: Emit code observations for functions, classes, imports, blocks, declarations, and malformed syntax regions.

### Task 9.2: Implement AST code candidate formation

- [ ] Step 9.2.1: Implement `AstCodeCandidateSet`.
- [ ] Step 9.2.2: Prefer AST-supported boundaries over line or token windows.
- [ ] Step 9.2.3: Use recursive split/merge only when oversized code units require it.
- [ ] Step 9.2.4: Produce repair or rejection records for syntax-breaking splits.

### Task 9.3: Implement code projection and fixtures

- [ ] Step 9.3.1: Implement `CodeProjection`.
- [ ] Step 9.3.2: Add relations for definitions, calls, imports, adjacency, and dependency context where admitted.
- [ ] Step 9.3.3: Add contradiction fixtures for nested functions/classes and code fences that look like prose structure.

## Phase 10: Add Semantic Refinement Without Making It Primary

### Task 10.1: Implement semantic shift observation from ADR-0006

- [ ] Step 10.1.1: Define semantic refinement policy flags and default them to optional or auto, not required.
- [ ] Step 10.1.2: Implement `SemanticShiftObservation`.
- [ ] Step 10.1.3: Add Sentence Transformers or Model2Vec adapter behind `EmbeddingPort`.
- [ ] Step 10.1.4: Keep embeddings and semantic model outputs as evidence, not source truth.

### Task 10.2: Implement semantic refinement candidate strategy

- [ ] Step 10.2.1: Implement `SemanticRefinementCandidateSet`.
- [ ] Step 10.2.2: Allow semantic refinement only after structural candidates exist.
- [ ] Step 10.2.3: Require evidence for weak or ambiguous structural regions before semantic refinement changes a boundary.
- [ ] Step 10.2.4: Add tests proving baseline chunking works without embeddings or LLM calls.

### Task 10.3: Add semantic contradiction and reproducibility checks

- [ ] Step 10.3.1: Record model identity and policy used for semantic observations.
- [ ] Step 10.3.2: Add fixtures where semantic similarity would merge source-distinct regions incorrectly.
- [ ] Step 10.3.3: Add audit output that distinguishes semantic evidence from structural evidence.

## Phase 11: Evaluate Candidate Quality And Strategy Tradeoffs

### Task 11.1: Implement candidate comparison

- [ ] Step 11.1.1: Implement `compare-strategies` output with candidate sets, hard gate results, soft metrics, rejections, repairs, and selected graph.
- [ ] Step 11.1.2: Include boundary clarity, chunk stickiness, context coherence, orphan count, repair count, semantic discontinuity, index cost estimate, and latency estimate.
- [ ] Step 11.1.3: Add benchmark fixtures for every strategy admitted so far.

### Task 11.2: Implement retrieval sanity evaluation

- [ ] Step 11.2.1: Define held-out retrieval sanity fixtures by source family.
- [ ] Step 11.2.2: Compare paragraph grouping, recursive fallback, dynamic token sizing, hierarchy, AST code, and semantic refinement.
- [ ] Step 11.2.3: Report quality and cost without letting benchmarks override hard invariants.

### Task 11.3: Expand source-family contradiction coverage

- [ ] Step 11.3.1: Add legal clause fixture with nested numbering.
- [ ] Step 11.3.2: Add transcript fixture with missing speaker labels.
- [ ] Step 11.3.3: Add scientific paper fixture with citation-heavy paragraphs.
- [ ] Step 11.3.4: Add definition/dependency fixture where “This means...” must stay near its referent.

## Phase 12: Add Specialized Modes Only After The Baseline Is Lawful

### Task 12.1: Admit late chunking only as a specialized mode

- [ ] Step 12.1.1: Add a policy flag for late chunking that defaults to false.
- [ ] Step 12.1.2: Require offline or premium indexing context before late chunking runs.
- [ ] Step 12.1.3: Preserve lineage, projection versioning, and rejection visibility in late chunking outputs.

### Task 12.2: Admit LLM-guided candidate formation only as boundary-assisted formation

- [ ] Step 12.2.1: Keep LLM providers behind boundary ports.
- [ ] Step 12.2.2: Treat LLM output as candidate evidence, never as accepted structure by authority.
- [ ] Step 12.2.3: Require audit records for prompt, policy, model identity, confidence, and rejected alternatives.

### Task 12.3: Keep chunk-free retrieval as research mode

- [ ] Step 12.3.1: Create an experimental policy namespace for chunk-free retrieval.
- [ ] Step 12.3.2: Prevent chunk-free experiments from weakening source, lineage, projection, or audit invariants.
- [ ] Step 12.3.3: Require a new ADR before chunk-free retrieval becomes a primary Catalyst mode.

## Phase 13: Documentation Completion And Release Readiness

### Task 13.1: Complete architecture documentation

- [ ] Step 13.1.1: Create `docs/ARCHITECTURE.md` explaining Catalyst's applied EBA layer map.
- [ ] Step 13.1.2: Create `docs/SYSTEM_LANGUAGE.md` with accepted nouns, rejected nouns, boundary-only terms, projection-only terms, and terms requiring ADRs.
- [ ] Step 13.1.3: Create `docs/INVARIANTS.md` with invariant names, enforcement locations, tests, and violation behavior.
- [ ] Step 13.1.4: Create `docs/BOUNDARIES.md` with ports, adapters, error translation, external assumptions, and security constraints.
- [ ] Step 13.1.5: Create `docs/PROJECTIONS.md` with schema versions, compatibility rules, lossy/lossless declarations, and deprecation policy.

### Task 13.2: Complete governance and CI

- [ ] Step 13.2.1: Wire import checks, native-name checks, file-size checks, invariant tests, boundary contract tests, projection schema checks, and contradiction tests into CI.
- [ ] Step 13.2.2: Ensure every invariant has unit tests.
- [ ] Step 13.2.3: Ensure every boundary adapter has contract tests.
- [ ] Step 13.2.4: Ensure every source family has contradiction fixtures.
- [ ] Step 13.2.5: Ensure every strategy has benchmark fixtures.

### Task 13.3: Define the first release acceptance gate

- [ ] Step 13.3.1: Prove a Markdown document can become an admitted chunk graph with retrieval and audit projections.
- [ ] Step 13.3.2: Prove fixed-size slicing does not run on the default path.
- [ ] Step 13.3.3: Prove every accepted chunk has source lineage.
- [ ] Step 13.3.4: Prove every public projection has a schema version.
- [ ] Step 13.3.5: Prove rejected candidates remain inspectable.
- [ ] Step 13.3.6: Prove no concrete boundary adapter is imported inward.
