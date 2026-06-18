<!-- **Catalyst** should be designed as an EBA-native chunk formation system, not as a splitter library.

The core decision is this:

> **Catalyst does not split text. Catalyst admits chunk structures from source evidence.**

This lines up directly with the EBA template: preserve source identity, observe without deciding, enforce invariants, form candidates, operate on admitted structures, project useful views, and keep boundaries external. The uploaded EBA template explicitly frames this as `source → observation → invariant → formation → operation → projection → boundary`, with source preservation, evidence-backed admission, rejected-structure inspection, and versioned projections as core goals. 

The [SOTA report](/Catalyst-Chunker_deep-research-report.md) points in the same direction: fixed-size slicing should not be Catalyst’s default; structure-aware, paragraph/header-first, adaptive, hierarchical, and AST-aware methods are the strongest practical center, with semantic and late-chunking methods treated as refinements or specialized modes rather than the foundation.  -->

# Catalyst Architecture

## One-sentence definition

**Catalyst is an invariant-first chunk formation engine that preserves source lineage, observes native document structure, forms competing chunk candidates, admits only evidence-backed chunk graphs, and projects task-specific views for retrieval, summarization, context assembly, code analysis, and audit.**

---

# 1. Architectural stance

Catalyst should not be organized around these names:

```text
ChunkService
ChunkManager
DocumentProcessor
SplitterPipeline
EmbeddingWorker
Repository
Controller
```

Those names import generic application architecture too early. EBA specifically warns against letting controllers, services, repositories, workers, pipelines, or framework conventions define the system before the internal structure has earned itself. 

Catalyst’s native concepts should be:

```text
SourceRecord
SourceSpan
SourceElement
Observation
EvidenceSet
Invariant
BoundaryCandidate
ChunkCandidate
ChunkSet
ChunkGraph
SelectionPolicy
RejectionRecord
RepairRecord
Projection
DecisionLedger
```

That vocabulary makes the system’s shape match the problem.

---

# 2. The actual system flow

```text
external input
  ↓
boundary adapter
  ↓
SourceRecord
  ↓
ObservationSet
  ↓
Invariant evaluation
  ↓
ChunkCandidateSet
  ↓
Candidate selection / rejection / repair
  ↓
Admitted ChunkGraph
  ↓
Versioned projections
  ↓
CLI / API / file export / retrieval index
```

Important distinction:

```text
Docling, Unstructured, Haystack, LlamaIndex, Tree-sitter, ast-grep, tokenizers, and embedding models are not Catalyst’s architecture.

They are boundary tools or observation instruments.
```

They may reveal evidence. They do not define truth.

---

# 3. Project layout

```text
catalyst/
├─ pyproject.toml
├─ README.md
├─ .importlinter
├─ catalyst.toml
│
├─ src/
│  └─ catalyst/
│     │
│     ├─ source/
│     │  ├─ records/
│     │  │  ├─ source_record.py
│     │  │  ├─ source_identity.py
│     │  │  ├─ source_span.py
│     │  │  └─ source_element.py
│     │  ├─ normalization/
│     │  │  ├─ normalization_policy.py
│     │  │  ├─ reversible_normalizer.py
│     │  │  └─ normalization_trace.py
│     │  └─ lineage/
│     │     ├─ lineage_map.py
│     │     ├─ offset_map.py
│     │     └─ provenance.py
│     │
│     ├─ observation/
│     │  ├─ instruments/
│     │  │  ├─ instrument.py
│     │  │  ├─ markdown_instrument.py
│     │  │  ├─ paragraph_instrument.py
│     │  │  ├─ sentence_instrument.py
│     │  │  ├─ table_instrument.py
│     │  │  ├─ code_ast_instrument.py
│     │  │  ├─ pdf_layout_instrument.py
│     │  │  ├─ semantic_shift_instrument.py
│     │  │  └─ tokenizer_instrument.py
│     │  ├─ evidence/
│     │  │  ├─ observation.py
│     │  │  ├─ evidence_set.py
│     │  │  ├─ confidence.py
│     │  │  └─ conflict.py
│     │  └─ reports/
│     │     └─ observation_report.py
│     │
│     ├─ invariant/
│     │  ├─ rules/
│     │  │  ├─ invariant.py
│     │  │  ├─ invariant_result.py
│     │  │  └─ invariant_registry.py
│     │  ├─ checks/
│     │  │  ├─ source_coverage_check.py
│     │  │  ├─ source_identity_check.py
│     │  │  ├─ offset_reversibility_check.py
│     │  │  ├─ token_budget_check.py
│     │  │  ├─ boundary_validity_check.py
│     │  │  ├─ table_integrity_check.py
│     │  │  ├─ code_syntax_boundary_check.py
│     │  │  └─ projection_schema_check.py
│     │  └─ ledger/
│     │     ├─ invariant_ledger.py
│     │     └─ violation_record.py
│     │
│     ├─ formation/
│     │  ├─ boundaries/
│     │  │  ├─ boundary_candidate.py
│     │  │  ├─ boundary_map.py
│     │  │  └─ boundary_score.py
│     │  ├─ candidates/
│     │  │  ├─ chunk_candidate.py
│     │  │  ├─ chunk_candidate_set.py
│     │  │  ├─ candidate_reason.py
│     │  │  └─ candidate_metrics.py
│     │  ├─ strategies/
│     │  │  ├─ paragraph_group_strategy.py
│     │  │  ├─ recursive_fallback_strategy.py
│     │  │  ├─ dynamic_token_strategy.py
│     │  │  ├─ hierarchical_strategy.py
│     │  │  ├─ semantic_refinement_strategy.py
│     │  │  ├─ ast_code_strategy.py
│     │  │  └─ late_chunking_strategy.py
│     │  ├─ selection/
│     │  │  ├─ selection_policy.py
│     │  │  ├─ selector.py
│     │  │  ├─ rejection_record.py
│     │  │  └─ decision_record.py
│     │  └─ repair/
│     │     ├─ orphan_repair.py
│     │     ├─ oversized_repair.py
│     │     ├─ table_repair.py
│     │     ├─ code_repair.py
│     │     └─ reconciliation.py
│     │
│     ├─ operation/
│     │  ├─ commands/
│     │  │  ├─ chunk_source.py
│     │  │  ├─ inspect_boundaries.py
│     │  │  ├─ evaluate_candidates.py
│     │  │  ├─ repair_chunk_graph.py
│     │  │  └─ emit_projection.py
│     │  ├─ transitions/
│     │  │  ├─ transition.py
│     │  │  ├─ transition_result.py
│     │  │  └─ transition_policy.py
│     │  └─ state/
│     │     ├─ catalyst_state.py
│     │     └─ run_record.py
│     │
│     ├─ projection/
│     │  ├─ chunks/
│     │  │  ├─ accepted_chunk.py
│     │  │  ├─ chunk_graph.py
│     │  │  └─ chunk_relation.py
│     │  ├─ views/
│     │  │  ├─ retrieval_view.py
│     │  │  ├─ parent_child_view.py
│     │  │  ├─ sentence_window_view.py
│     │  │  ├─ summary_view.py
│     │  │  ├─ code_view.py
│     │  │  └─ audit_view.py
│     │  ├─ schemas/
│     │  │  ├─ schema_version.py
│     │  │  ├─ public_schema.py
│     │  │  └─ error_envelope.py
│     │  └─ exporters/
│     │     ├─ jsonl_export.py
│     │     ├─ markdown_export.py
│     │     ├─ sqlite_export.py
│     │     └─ vector_index_export.py
│     │
│     ├─ boundary/
│     │  ├─ ports/
│     │  │  ├─ source_loader.py
│     │  │  ├─ artifact_writer.py
│     │  │  ├─ tokenizer_port.py
│     │  │  ├─ embedding_port.py
│     │  │  ├─ document_parser_port.py
│     │  │  ├─ ast_parser_port.py
│     │  │  └─ telemetry_sink.py
│     │  ├─ adapters/
│     │  │  ├─ filesystem/
│     │  │  ├─ docling/
│     │  │  ├─ unstructured/
│     │  │  ├─ haystack/
│     │  │  ├─ llamaindex/
│     │  │  ├─ tree_sitter/
│     │  │  ├─ ast_grep/
│     │  │  ├─ tokenizers/
│     │  │  ├─ tiktoken/
│     │  │  ├─ blingfire/
│     │  │  └─ sentence_transformers/
│     │  └─ presentation/
│     │     ├─ cli/
│     │     └─ api/
│     │
│     ├─ policy/
│     │  ├─ architecture_policy.py
│     │  ├─ naming_policy.py
│     │  ├─ dependency_policy.py
│     │  ├─ source_policy.py
│     │  ├─ formation_policy.py
│     │  ├─ projection_policy.py
│     │  └─ quality_policy.py
│     │
│     └─ shared/
│        ├─ ids.py
│        ├─ result.py
│        ├─ errors.py
│        └─ typing.py
│
├─ governance/
│  ├─ tools/
│  │  ├─ enforce_imports.py
│  │  ├─ enforce_file_size.py
│  │  ├─ enforce_native_names.py
│  │  ├─ enforce_projection_contracts.py
│  │  ├─ enforce_invariant_coverage.py
│  │  └─ enforce_boundary_purity.py
│  └─ policies/
│     ├─ architecture_contracts.md
│     ├─ naming_policy.md
│     ├─ invariant_policy.md
│     ├─ admission_policy.md
│     ├─ boundary_policy.md
│     ├─ projection_policy.md
│     └─ testing_policy.md
│
├─ tests/
│  ├─ unit/
│  ├─ contract/
│  ├─ contradiction/
│  ├─ integration/
│  └─ e2e/
│
└─ docs/
   ├─ ARCHITECTURE.md
   ├─ SYSTEM_LANGUAGE.md
   ├─ INVARIANTS.md
   ├─ BOUNDARIES.md
   ├─ PROJECTIONS.md
   ├─ DECISION_LEDGER.md
   └─ ADRs/
```

---

# 4. Layer design

## `source/`

Purpose:

> Preserve what was received before any chunking claim is made.

Source owns:

```text
SourceRecord
SourceIdentity
SourceSpan
SourceElement
NormalizationTrace
LineageMap
OffsetMap
Provenance
```

A `SourceRecord` should preserve:

```python
@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    source_kind: str
    raw_bytes_hash: str
    canonical_text: str
    canonical_text_hash: str
    metadata: dict[str, Any]
    normalization_trace_id: str | None
```

A `SourceSpan` should preserve:

```python
@dataclass(frozen=True)
class SourceSpan:
    source_id: str
    start_byte: int | None
    end_byte: int | None
    start_char: int
    end_char: int
    page_number: int | None = None
    line_start: int | None = None
    line_end: int | None = None
    element_id: str | None = None
```

This layer must not know anything about embeddings, retrieval, vector stores, Docling, Haystack, APIs, or CLI behavior.

---

## `observation/`

Purpose:

> Record what can be seen without deciding what the chunks are.

Observation instruments produce evidence only.

Examples:

```text
MarkdownHeadingObservation
ParagraphBoundaryObservation
SentenceBoundaryObservation
ListAdjacencyObservation
TableRegionObservation
TableHeaderObservation
CodeFunctionObservation
CodeClassObservation
SemanticShiftObservation
TokenCountObservation
PDFPageHeaderObservation
MalformedRegionObservation
```

Core type:

```python
@dataclass(frozen=True)
class Observation:
    observation_id: str
    kind: str
    span: SourceSpan
    confidence: float
    weight: float
    instrument: str
    payload: dict[str, Any]
```

This keeps the SOTA tools in their proper place. Docling, Unstructured, LlamaIndex, Haystack, Tree-sitter, and ast-grep can all help observe structure, but Catalyst should treat their outputs as evidence, not authority. The research report specifically recommends structure-first parsing, local semantic refinement only where needed, and AST-aware chunking for code. 

---

## `invariant/`

Purpose:

> Reject malformed or dishonest structures.

Catalyst’s core invariants should be strict.

### Required invariants

```text
I001 Source Coverage
Every accepted chunk graph must cover every required source span exactly once unless a lossy mode declares omissions.

I002 Source Lineage
Every accepted chunk must map back to source identity and source spans.

I003 Reversible Normalization
Every normalized span must be traceable to raw source or explicitly marked lossy.

I004 Observation Purity
Observation cannot mutate source records or admit chunk structures.

I005 Candidate Evidence
Every accepted chunk candidate must cite observations, policy, or repair records.

I006 Boundary Validity
Accepted chunk boundaries must be supported by boundary evidence or explicit fallback policy.

I007 Token Budget Honesty
Token limits may refine structure but cannot silently erase source material.

I008 Table Integrity
Table chunks must preserve header/body relationships or record why they were split.

I009 Code Boundary Integrity
Code chunks must prefer AST structure over line windows, and syntax-breaking splits require repair or rejection.

I010 Projection Versioning
Every public output must include schema_version and projection_kind.

I011 Rejection Visibility
Rejected candidates must produce rejection records.

I012 Boundary Purity
Concrete external tools cannot define Catalyst’s native identity, invariants, or accepted structures.
```

The research report names almost the same invariants for a Catalyst-like EBA system: source offsets or native element IDs, reproducibility from source plus policy, no silent dropping of table headers/page headers/code boundaries, reversible traces for token refinements, and projection disclosure. 

---

## `formation/`

Purpose:

> Generate, compare, repair, reject, and admit chunk structures.

Formation is the heart of Catalyst.

It should not produce one chunk set directly. It should produce competing candidate sets:

```text
ParagraphGroupCandidateSet
RecursiveFallbackCandidateSet
DynamicTokenCandidateSet
HierarchicalCandidateSet
SemanticRefinementCandidateSet
AstCodeCandidateSet
LateChunkingCandidateSet
```

The SOTA report supports this exact center: paragraph/header-first and structure-aware strategies are the default; dynamic token sizing is a strong efficiency trade-off; hierarchical parent/child projections are valuable; semantic splitting is useful but should be a refinement; AST-aware chunking should be the code default; late chunking and LLM-guided chunking should be specialized modes. 

### Candidate scoring

Catalyst should score candidates using both hard gates and soft metrics.

Hard gates:

```text
source coverage
source lineage
token hard max
table integrity
code syntax boundary
projection schema readiness
rejection visibility
```

Soft metrics:

```text
boundary clarity
chunk stickiness
context coherence
size variance
orphan count
repair count
semantic discontinuity
retrieval sanity score
index cost estimate
latency estimate
```

MoC’s **Boundary Clarity** and **Chunk Stickiness** are especially useful as native Catalyst metrics, even if Catalyst does not use MoC’s full LLM-heavy approach. The research report calls these concepts directly useful for evaluating chunk quality. 

### Selection policy

```python
@dataclass(frozen=True)
class SelectionPolicy:
    mode: str
    hard_max_tokens: int
    target_tokens: int
    prefer_structure: bool
    allow_semantic_refinement: bool
    allow_late_chunking: bool
    require_ast_for_code: bool
    max_repair_ratio: float
    max_orphan_ratio: float
```

Default policy:

```yaml
selection:
  mode: retrieval
  hard_max_tokens: 1200
  target_tokens: 650
  prefer_structure: true
  allow_semantic_refinement: true
  allow_late_chunking: false
  require_ast_for_code: true
  max_repair_ratio: 0.10
  max_orphan_ratio: 0.02
```

---

## `operation/`

Purpose:

> Execute explicit system actions over admitted structures.

Operations should be named as commands, not generic services.

Good operations:

```text
chunk-source
inspect-boundaries
evaluate-candidates
repair-chunk-graph
emit-projection
explain-chunk
compare-strategies
audit-run
```

Bad operations:

```text
process-document
run-pipeline
manage-chunks
handle-request
```

Example command flow:

```text
ChunkSource
  → load SourceRecord through boundary port
  → observe source
  → evaluate invariants
  → form candidate sets
  → select admitted ChunkGraph
  → emit requested projections
  → write artifacts through boundary port
```

The operation layer may import boundary **ports** when it needs external capability, but it must never import concrete adapters. That matches the EBA dependency rule: concrete adapters stay outside internal layers. 

---

## `projection/`

Purpose:

> Render admitted structures into stable outputs.

Catalyst needs plural projections because one chunk shape will not serve all downstream tasks.

Required projections:

```text
RetrievalProjection
ParentChildProjection
SentenceWindowProjection
SummaryProjection
CodeProjection
AuditProjection
BoundaryInspectionProjection
TrainingDataProjection
```

The research report explicitly recommends plural projections: precise retrieval view, larger context-window or parent view, and audit view with lineage and rejection records. 

### Retrieval projection

For vector search or BM25/hybrid search:

```json
{
  "schema_version": "catalyst.retrieval.v1",
  "projection_kind": "retrieval",
  "chunk_id": "chk_...",
  "source_id": "src_...",
  "text": "...",
  "token_count": 642,
  "source_spans": [],
  "heading_path": [],
  "relations": {
    "parent": "chunk_parent_...",
    "previous": "chunk_prev_...",
    "next": "chunk_next_..."
  },
  "warnings": [],
  "omissions": []
}
```

### Audit projection

For explainability:

```json
{
  "schema_version": "catalyst.audit.v1",
  "projection_kind": "audit",
  "source_id": "src_...",
  "coverage": {
    "required_source_spans": 184,
    "covered_source_spans": 184,
    "lost_spans": 0
  },
  "candidate_sets": [],
  "accepted_candidate_set": "paragraph_group_with_recursive_repair",
  "rejections": [],
  "repairs": [],
  "violations": [],
  "warnings": []
}
```

### Boundary inspection projection

For debugging chunk decisions:

```json
{
  "schema_version": "catalyst.boundaries.v1",
  "projection_kind": "boundary_inspection",
  "boundary_candidates": [
    {
      "position": 18432,
      "accepted": true,
      "score": 0.88,
      "evidence": ["heading", "paragraph_break", "topic_shift"],
      "penalties": []
    }
  ]
}
```

---

## `boundary/`

Purpose:

> Keep external systems useful but subordinate.

Boundary adapters:

```text
Docling adapter
Unstructured adapter
Haystack adapter
LlamaIndex adapter
Tree-sitter adapter
ast-grep adapter
Hugging Face Tokenizers adapter
tiktoken adapter
Bling Fire adapter
Sentence Transformers adapter
Model2Vec adapter
filesystem adapter
sqlite adapter
jsonl adapter
cli adapter
api adapter
```

The research report recommends Docling as the strongest local document/PDF front end, Unstructured as a close alternative, Haystack and LlamaIndex as useful chunking orchestration/building-block libraries, Tree-sitter/ast-grep for code, and fast tokenizers for CPU-friendly alignment. 

Boundary rule:

```text
External tools can provide observations, token counts, parsed elements, embeddings, and exported artifacts.

External tools cannot define Catalyst’s internal truth.
```

---

# 5. Default strategy matrix

Catalyst should choose strategy by source family.

| Source family       | Primary strategy                        | Refinement                                  | Projection                  |
| ------------------- | --------------------------------------- | ------------------------------------------- | --------------------------- |
| Markdown            | Header/paragraph grouping               | Recursive fallback, optional semantic shift | Retrieval + parent/child    |
| Plain text          | Paragraph grouping                      | Sentence grouping, dynamic token sizing     | Retrieval + sentence window |
| PDF                 | Docling structural elements             | Table repair, header/footer detection       | Retrieval + audit           |
| HTML                | DOM-aware element grouping              | Boilerplate removal with trace              | Retrieval + summary         |
| Legal docs          | Section/clause grouping                 | Paragraph group, citation preservation      | Retrieval + audit           |
| Scientific papers   | Section/paragraph/table/figure grouping | Dynamic token, citation preservation        | Retrieval + parent/child    |
| Code                | AST-aware chunking                      | Recursive split/merge                       | Code projection             |
| Transcripts         | Speaker turn grouping                   | Question/answer and topic shift detection   | Retrieval + summary         |
| Long books          | Hierarchical sections                   | Parent/child plus dynamic token             | Parent/child + summary      |
| Weak structure docs | Paragraph fallback                      | Local semantic refinement                   | Retrieval + sentence window |

Default priority:

```text
1. Source-native structure
2. Paragraph/header grouping
3. AST boundaries for code
4. Recursive fallback
5. Dynamic token sizing
6. Optional semantic refinement
7. Hierarchical parent/child projection
8. Sentence-window context recovery
9. Late chunking only for offline premium indexing
10. LLM-guided chunking only as specialized boundary-assisted formation
```

This directly follows the report’s practical recommendation: structure-aware first, small local semantic pass only where needed, hierarchical/sentence-window projections instead of blanket overlap, and AST-aware code chunking rather than line windows. 

---

# 6. Chunk graph model

Catalyst should emit a graph, not a flat list.

```python
@dataclass(frozen=True)
class AcceptedChunk:
    chunk_id: str
    source_id: str
    spans: tuple[SourceSpan, ...]
    text: str
    token_count: int
    chunk_kind: str
    candidate_set_id: str
    evidence_ids: tuple[str, ...]
    warning_ids: tuple[str, ...]
```

```python
@dataclass(frozen=True)
class ChunkRelation:
    source_chunk_id: str
    target_chunk_id: str
    relation_kind: str
    evidence_ids: tuple[str, ...]
```

Relation kinds:

```text
parent_of
child_of
previous_sibling
next_sibling
continues
depends_on
defines
example_of
table_header_for
citation_supports
code_imports_for
code_calls
summary_of
retrieval_window_for
```

Graph output:

```python
@dataclass(frozen=True)
class ChunkGraph:
    graph_id: str
    source_id: str
    chunks: tuple[AcceptedChunk, ...]
    relations: tuple[ChunkRelation, ...]
    formation_policy_id: str
    invariant_result_ids: tuple[str, ...]
    decision_record_ids: tuple[str, ...]
```

---

# 7. Overlap policy

Catalyst should not use dumb overlap as the default.

Bad default:

```text
chunk_size = 800
overlap = 150
```

Catalyst default:

```text
precise chunks
plus parent/child recovery
plus sentence-window projection
plus dependency-specific context
```

The research report explicitly recommends precise chunks plus sentence-window or parent/child recovery over always-on overlap, because it keeps formation cleaner and index size smaller. 

Use overlap only when earned by evidence:

```text
pronoun dependency
definition dependency
citation dependency
table continuation
speaker-turn continuation
code import dependency
claim/example dependency
```

---

# 8. CLI design

Catalyst should be CLI-first but not CLI-shaped internally.

```bash
catalyst chunk ./docs \
  --mode retrieval \
  --out ./out/chunks.jsonl \
  --audit ./out/audit.json

catalyst inspect-boundaries ./docs/report.pdf \
  --out ./out/boundaries.json

catalyst compare-strategies ./docs \
  --strategies paragraph,recursive,hierarchical,semantic \
  --out ./out/strategy_report.json

catalyst chunk-code ./src \
  --lang py \
  --out ./out/code_chunks.jsonl

catalyst explain-chunk ./out/chunks.jsonl chk_01HF...

catalyst audit ./out/audit.json
```

Config:

```yaml
catalyst:
  mode: retrieval

source:
  require_lineage: true
  lossy_mode: false

observation:
  instruments:
    markdown: true
    paragraph: true
    sentence: true
    table: true
    code_ast: true
    semantic_shift: auto
    tokenizer: true

formation:
  candidate_sets:
    paragraph_group: true
    recursive_fallback: true
    dynamic_token: true
    hierarchical: true
    semantic_refinement: auto
    ast_code: true
    late_chunking: false

tokens:
  target: 650
  soft_min: 250
  soft_max: 950
  hard_max: 1200

projection:
  retrieval: true
  parent_child: true
  sentence_window: true
  audit: true

governance:
  keep_rejections: true
  fail_on_lost_source: true
  fail_on_unversioned_projection: true
  fail_on_boundary_adapter_import_inward: true
```

---

# 9. Governance

Use EBA governance aggressively.

Required gates:

```text
1. Import direction enforced.
2. No concrete boundary adapters imported inward.
3. No public projection without schema_version.
4. No accepted chunk without source lineage.
5. No rejected candidate discarded silently.
6. No observation mutates source.
7. No file over 500 LOC without split or ADR.
8. No vague names without ADR.
9. Every invariant has unit tests.
10. Every boundary adapter has contract tests.
11. Every source family has contradiction fixtures.
12. Every strategy has benchmark fixtures.
```

The EBA template recommends exactly this kind of governance plane: import enforcement, native-name enforcement, invariant ledgers, boundary purity, projection contracts, contradiction tests, and docs like `ARCHITECTURE.md`, `SYSTEM_LANGUAGE.md`, `INVARIANTS.md`, `BOUNDARIES.md`, `PROJECTIONS.md`, and `DECISION_LEDGER.md`. 

---

# 10. Contradiction tests

Catalyst needs tests that try to trick it into false structure.

Fixtures:

```text
PDF with repeated page headers that look like headings
Markdown with fake headings inside code fences
Table split across pages
Legal clause with nested numbering
Transcript with speaker labels missing
Scientific paper with citation-heavy paragraphs
Code file with nested functions/classes
Malformed JSON inside Markdown
OCR text with hyphenation artifacts
Very short paragraphs that should merge
Very long paragraph that must split safely
Paragraph starting with “This means...”
Definition separated from first use
```

Questions each test asks:

```text
Did Catalyst preserve source coverage?
Did it reject false headings?
Did it avoid splitting inside code fences?
Did it preserve table headers?
Did it keep definitions near dependent text?
Did it record uncertain candidates?
Did it version the projection?
Did it keep boundary tools from defining internal identity?
```

---

# 11. MVP implementation order

Build Catalyst in this order:

```text
1. source/
   SourceRecord, SourceSpan, SourceIdentity, LineageMap.

2. observation/
   Markdown, paragraph, sentence, tokenizer observations.

3. invariant/
   Source coverage, lineage, token budget, projection versioning.

4. formation/
   ParagraphGroupCandidateSet and RecursiveFallbackCandidateSet.

5. projection/
   RetrievalProjection and AuditProjection.

6. operation/
   chunk-source and inspect-boundaries commands.

7. boundary/
   filesystem CLI, JSONL writer, tokenizer adapter.

8. governance/
   import-linter, native naming check, projection schema check.

9. richer documents/
   Docling adapter for PDF/document structure.

10. hierarchy/
   ParentChildProjection and hierarchical candidate strategy.

11. code/
   Tree-sitter or ast-grep adapter and AstCodeCandidateSet.

12. semantic refinement/
   Sentence Transformers or Model2Vec boundary refinement.

13. evaluation/
   candidate comparison, boundary clarity, chunk stickiness, retrieval sanity.

14. specialized modes/
   late chunking, LLM-guided candidate formation, chunk-free experiments.
```

Do not start with embeddings. Start with source, spans, observations, invariants, and structural candidates.

---

# 12. First ADRs

Catalyst should begin with these ADRs:

```text
ADR-0001: Catalyst uses EBA layer admission, not service/repository architecture.
ADR-0002: Source lineage is mandatory for every accepted chunk.
ADR-0003: Fixed-size slicing is fallback only, never default.
ADR-0004: Structure-first paragraph/header grouping is the default prose strategy.
ADR-0005: Code chunking requires AST-aware observation by default.
ADR-0006: Semantic chunking is a refinement strategy, not the primary strategy.
ADR-0007: Retrieval uses parent/child and sentence-window recovery instead of blanket overlap.
ADR-0008: Docling is admitted as a boundary adapter, not as an internal model.
ADR-0009: Public projections require schema versions.
ADR-0010: Rejected candidates remain inspectable.
```

---

# Final shape

Catalyst should be overbuilt in exactly one way: **it should overbuild the evidence, lineage, candidate, invariant, and projection machinery.**

It should not overbuild by stacking frameworks or adding LLM segmentation too early.

The strongest design is:

```text
Catalyst
  = source-preserving
  + observation-driven
  + invariant-checked
  + multi-candidate
  + structure-first
  + token-aware
  + hierarchy-capable
  + AST-aware for code
  + semantic only when useful
  + projection-plural
  + audit-native
  + boundary-pure
```

That gives you a serious tool instead of another wrapper around `split_text(text, chunk_size, overlap)`.
