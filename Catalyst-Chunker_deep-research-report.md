# Modern Chunking for Constrained CLI Systems Through Emergence Based Architecture

## Executive judgment

The strongest current evidence does **not** support fixed-size character slicing as a default. The broadest recent benchmark the field has so far produced evaluated 36 chunking strategies across 6 domains and 5 embedding models, and found that content-aware approaches consistently beat naive fixed baselines. In that study, **Paragraph Group Chunking** had the best overall retrieval effectiveness, while **Dynamic Token Size Chunking** offered one of the best effectiveness–efficiency trade-offs. Fixed character chunking trailed badly. citeturn32view0turn33view1turn33view2

Through your EBA lens, that result is highly coherent: the best chunkers are usually the ones that let structure emerge from the source material instead of forcing an a priori layout. In practice, on constrained non-GPU hardware, the most defensible default is a **structure-first pipeline**: parse documents into native elements, preserve lineage and offsets, group by paragraphs/headers/tables/code units, and only then apply lightweight token-aware or semantic refinements where the source actually shows ambiguity. That is much closer to *source → observation → invariant → formation* than a generic “split every N tokens” template. citeturn17view0turn18view0turn29view1turn32view0

The practical recommendation is therefore:

1. **Use structure-aware chunking first** for prose, technical docs, PDFs, tables, and Markdown.
2. **Add a small local semantic pass** only where simple structural grouping is clearly insufficient.
3. **Use hierarchical or sentence-window projections** instead of reflexively adding overlap everywhere.
4. **Use AST-aware chunking for code**, not line windows.
5. Treat **late chunking** and **chunk-free retrieval** as important frontiers, but not as the primary default on constrained CPU-only systems. citeturn24view0turn14view1turn34view0turn35view1turn37view0

## What the current research actually shows

The most useful recent macro-level result is the 2026 cross-domain benchmark. It reports that chunking materially affects retrieval quality, memory, index size, and latency, and that **structure-preserving and adaptive methods frequently outperform fixed-size baselines**. It also shows that there is no single universal winner across all domains, but some patterns are stable: paragraph grouping is strongest in legal and mathematics-heavy corpora, while dynamic token sizing is especially strong in biology, physics, and health. Larger embedding models help, but they do **not** rescue bad chunking; segmentation quality and embedding quality were complementary rather than interchangeable. citeturn32view0turn33view1turn33view2

That same study is especially relevant for constrained systems because it did not only score retrieval quality; it also measured efficiency. Its conclusion is operationally important: very fine-grained methods can increase recall, but they often do so by exploding chunk counts, index size, and latency. Paragraph Group Chunking sat near the Pareto frontier, while Dynamic Token Chunking offered a strong balance of quality and cost. LLM-driven segmentation and some heavy semantic methods incurred much larger preprocessing costs. citeturn33view1turn33view2

Recent ACL work sharpens the picture. **AutoChunker** argues for a bottom-up, hierarchy-preserving approach that explicitly optimizes noise reduction, completeness, context coherence, task relevance, and retrieval performance, and reports gains over prior baselines on support and Wikipedia-style documents. **MoC** adds two directly useful chunk-quality ideas—**Boundary Clarity** and **Chunk Stickiness**—and shows why purely traditional and purely semantic methods can both fail on complex contextual transitions. Those papers matter even if you do not adopt their full LLM-heavy methods, because they provide a better vocabulary for what “good chunking” actually means. citeturn36view0turn36view1

Two other lines of work mark the frontier beyond classical chunking. **Late Chunking** embeds long text before pooling smaller chunk spans, which preserves cross-chunk context and improved retrieval scores over naive chunking in the paper’s evaluations. **Chunk-free methods** like CFIC and Landmark Embedding go further by trying to avoid conventional chunking altogether or by generating sentence-level representations from coherent long context. These are real advances, but they depend on long-context encoders or hidden-state retrieval machinery that are much less natural for a minimal, CPU-first, CLI-centric pipeline. citeturn34view0turn35view0turn35view1

For code, the evidence is even clearer. The 2025 **cAST** paper shows that AST-based recursive split-and-merge chunking improves retrieval and downstream code generation over line-based chunking, precisely because it preserves functions, classes, and syntactic boundaries. That is almost a textbook EBA result: the chunk boundary is admitted by the language’s own structure, not by a generic window. citeturn37view0

## Strategy families that fit constrained CLI environments

The table below separates what is **research-strong** from what is **hardware-realistic**.

| Strategy family | What it does | Evidence signal | CPU/CLI fit | EBA fit |
|---|---|---|---|---|
| **Structure-first paragraph/header grouping** | Uses paragraphs, headings, sections, tables, document elements as primary boundaries | Best broad retrieval results in current cross-domain benchmark for paragraph grouping; official doc tools preserve document-native structure and metadata citeturn32view0turn33view1turn17view0turn18view0 | **Excellent** | **Excellent** |
| **Recursive separator chunking** | Applies progressively finer separators until size constraints are satisfied | Strong practical baseline; preserves higher-order boundaries before falling back to smaller ones citeturn29view0 | **Excellent** | **Good** |
| **Hierarchical parent/child chunking** | Builds coarse and fine chunks together for multi-resolution retrieval | Supported by Haystack and supported conceptually by recent hierarchical research and benchmark categories citeturn29view1turn32view0 | **Very good** | **Excellent** |
| **Embedding-based semantic chunking** | Splits when local semantic similarity drops | Useful, modern, and available in CPU-friendly frameworks, but more expensive than structural grouping and not always the best global trade-off citeturn24view0turn16view0turn32view0turn36view1 | **Good** with small local models | **Good** when used as refinement |
| **Late chunking** | Computes chunk embeddings from token representations of longer context | Important frontier with better context retention than naive chunking, but inherently heavier because it needs long-context embedding passes citeturn34view0 | **Fair** for offline batch jobs, **poor** as a default on weak CPUs | **Good**, but expensive |
| **LLM-guided chunking** | Uses an LLM to infer logical boundaries directly | AutoChunker and MoC show benefits, but recent benchmarks also show much higher preprocessing cost for LLM-driven approaches citeturn36view0turn36view1turn33view2 | **Poor** on constrained local hardware | Conceptually strong, operationally weak |
| **AST-aware code chunking** | Uses syntax trees, then recursive split/merge | Strong code-specific evidence from cAST citeturn37view0 | **Excellent** with local parsers | **Excellent** |

From a constrained-system perspective, the highest-value modern combination is usually:

**structure-aware grouping + token-aware normalization + optional semantic refinement + hierarchical projection**. That combination captures most of the current literature’s upside without importing the computational profile of long-context or LLM-driven chunkers. citeturn17view0turn24view0turn29view0turn29view1turn32view0

## Tooling that is practical today from the CLI

The most mature CPU-friendly document front end is currently **Docling**. Its CLI can convert local files, directories, or URLs into Markdown, JSON, YAML, HTML, and text. Its chunking model is especially relevant to your EBA framing because it distinguishes a **HierarchicalChunker** from a **HybridChunker**: the hierarchical pass uses document structure and metadata, while the hybrid pass adds tokenizer-aware split/merge refinements on top of that structure. It can repeat table headers across table chunks, and it explicitly supports offline model prefetching via `docling-tools models download`, `--artifacts-path`, and `DOCLING_ARTIFACTS_PATH`. In Docling’s technical report, it also led the compared tools on CPU PDF parsing speed, reporting 3.1 sec/page on x86 CPU versus 4.2 sec/page for Unstructured in their benchmark. citeturn19view0turn17view0turn20view1turn20view2turn12view3

A close alternative is **Unstructured**. Its chunking logic is element-based rather than plain-text-first: partitioning identifies document elements, and chunking combines those elements while preserving semantic units where possible. Its `basic` strategy maximally packs sequential elements; its `by_title` strategy preserves section boundaries and can optionally respect page boundaries. Importantly for lineage and reversibility, chunk metadata can retain `orig_elements`, which is exactly the kind of traceability an invariant-first architecture wants. citeturn18view0

For local chunking orchestration, **Haystack** is one of the strongest CPU-friendly options even though it is library-first rather than a standalone chunking CLI. It exposes:
- `DocumentSplitter` for word/sentence/passage/page/line/function splitting,
- `RecursiveDocumentSplitter` for ordered separator fallback,
- `HierarchicalDocumentSplitter` for parent/child trees,
- `EmbeddingBasedDocumentSplitter` for local semantic break detection using cosine distances over sequential sentence groups,
- `SentenceWindowRetriever` for retrieving local context around precise small chunks. citeturn29view2turn29view0turn29view1turn24view0turn14view1

That last point matters. On constrained hardware, the best answer to “but what about lost context?” is often **not** more overlap. It is often better to index tighter chunks and then retrieve a context window at query time. Haystack’s `SentenceWindowRetriever` is explicitly designed for that pattern, returning neighboring sentences around a matched sentence while keeping the embedded unit precise. citeturn14view0turn14view1

**LlamaIndex** is also useful, especially for source-native parsers. Its `MarkdownNodeParser` preserves header paths as metadata. Its `SentenceSplitter` prefers complete sentences and paragraphs. Its `SemanticSplitterNodeParser` performs sentence-group embedding comparisons using a configurable buffer size and percentile-based dissimilarity breakpoint threshold. These are helpful building blocks when you want to keep a CLI boundary but still expose more than one candidate chunker inside your formation layer. citeturn15view1turn12view2turn16view0

For tokenization on CPU, three tools matter:
- **Hugging Face Tokenizers**, which are Rust-based, very fast on CPU, and preserve full alignment tracking back to original text.
- **tiktoken**, which OpenAI describes as a fast BPE tokenizer and benchmarks as 3–6× faster than a comparable open-source tokenizer in its README.
- **Bling Fire**, which Microsoft positions as a very fast tokenizer/sentence breaker with ready Python bindings. citeturn21view0turn26search0turn21view1

For code, the strongest practical route is **Tree-sitter** plus a thin CLI layer. Tree-sitter provides widely used parsing primitives and official Python bindings; its CLI can build and use parsers. **ast-grep** gives you a ready-made AST-native CLI on top of Tree-sitter, including `run`, `scan`, and `test`, and supports many languages. That is enough to build EBA-style observation and boundary-candidate generation for code before you ever reach vectorization. citeturn13search0turn13search1turn21view2turn22view0turn12view5

Two small but important performance notes for semantic refinement on weak CPUs:

Small local embedding models can be run explicitly on CPU in Sentence Transformers, and the official docs also note ONNX support for CPU acceleration. If you really need a more aggressive CPU-first semantic pass, **Model2Vec** is an interesting emerging option: its authors report static embedding models that are much smaller and much faster than the distilled sentence-transformer source model, with CPU-friendly inference and lightweight dependencies. I would treat that as a promising accelerator for semantic boundary detection, not as your primary chunking philosophy. citeturn25search1turn25search3turn28view0

### Minimal CLI-first patterns

A clean offline PDF/document front end with Docling:

```bash
docling-tools models download
docling convert --to json --to md --artifacts-path "$HOME/.cache/docling/models" ./docs
```

That gives you a local, schema-bearing source representation before chunk formation begins. Docling explicitly supports local artifacts paths and offline usage. citeturn19view0turn20view1turn20view2

A CPU-local semantic refinement stage with Haystack from the shell via a tiny Python entrypoint:

```bash
python -m catalyst.chunk_semantic ./docs/*.md
```

Inside that module, `EmbeddingBasedDocumentSplitter` can use a local Sentence Transformers embedder to split by sentence-group similarity, with `percentile`, `min_length`, and `max_length` controls. citeturn24view0turn25search1turn25search3

A syntax-aware code observation boundary with ast-grep:

```bash
ast-grep scan -c sgconfig.yml ./src
```

or one-shot:

```bash
ast-grep run --lang py --pattern 'def $NAME($$$ARGS): $$$BODY' ./src
```

ast-grep is explicitly a CLI for AST-based searching, linting, and rewriting, and is backed by Tree-sitter parsers. citeturn12view5turn22view0

## What this looks like in Emergence Based Architecture

Your EBA frame is unusually well matched to chunking because chunking is not naturally “controller/service/repository” work. It is closer to *lawful structure formation from source material*. The modern chunking literature points in the same direction: good systems preserve document-native units, expose chunk-quality metrics, keep lineage, and distinguish source structure from convenience boundaries. citeturn36view0turn36view1turn17view0turn18view0

In EBA terms, the mapping is straightforward.

**Source** should hold canonical documents, paragraph spans, heading paths, table boundaries, page numbers, token offsets, and source identities. Docling and Unstructured both expose native document elements and metadata that support this. Haystack and LlamaIndex both propagate source IDs and split indices in metadata. citeturn17view0turn18view0turn24view0turn29view2turn15view1

**Observation** should detect only what the source is revealing: headings, repeated headers, list adjacency, table continuations, code boundaries, sentence transitions, semantic-distance spikes, and malformed regions. LlamaIndex semantic splitting, Haystack embedding-based splitting, Docling’s hierarchical/hybrid chunkers, and Tree-sitter/ast-grep for code all fit here as instruments rather than truth-makers. citeturn16view0turn24view0turn17view0turn13search0turn22view0

**Invariant** is the most important layer. Based on both the research and the official tooling semantics, the invariants I would enforce are:

- every output chunk must map to source offsets or source-native element IDs;
- chunk formation must be reproducible from source plus policy;
- no structure-aware pass may silently drop table headers, page headers, or code boundaries without logging why;
- every token-sized refinement must preserve a reversible trace to the parent structural unit;
- every projection must disclose whether it is parent, child, semantic, or retrieval-window context. citeturn18view0turn17view0turn29view1turn14view1

**Formation** should generate multiple candidate chunk graphs, not one blessed splitter. A realistic constrained candidate set is:
- paragraph-group structural candidates,
- recursive fallback candidates,
- lightweight semantic refinement candidates,
- hierarchy parent/child candidates,
- AST candidates for code.  
Then score each candidate set against invariants and lightweight metrics such as coverage, variance of chunk size, boundary clarity, and retrieval sanity checks on held-out queries. The MoC and AutoChunker papers are useful here mainly because they supply chunk-quality concepts that belong in your evaluation ledger even if you do not adopt their full generation-time machinery. citeturn36view0turn36view1turn32view0

**Operation** should remain explicit. “Chunk document,” “inspect boundaries,” “repair malformed chunk set,” and “emit retrieval projection” are better EBA operations than a vague `ChunkService`. Haystack’s hierarchy and sentence-window mechanisms support exactly this kind of explicit multi-stage operation: index precise units, then recover broader windows or merged parents when actually needed. citeturn29view1turn14view1

**Projection** should be plural. A constrained system should usually store at least three projections:
- a precise retrieval view,
- a larger context-window or parent view,
- an audit view with lineage and rejection records.  
This follows directly from the observation that small chunks and large chunks optimize different things. The retrieval literature now treats that trade-off as central, not incidental. citeturn33view1turn33view2turn14view1

## Final recommendation

For a Catalyst-like system built around EBA, I would recommend the following default policy.

Use **Docling** as the source-normalization boundary for documents and PDFs when you need strong local structure recovery and an actual CLI. Use its **HierarchicalChunker** or **HybridChunker** as the primary formation mechanism for prose-heavy and richly structured documents. This is the cleanest current fit for *discovered invariants first, token limits second*. citeturn19view0turn17view0turn20view1turn12view3

For plain text and Markdown, use a **paragraph/header-first strategy** with a **recursive fallback**, then optionally add a **small local embedding-based refinement** only when the document shows weak structural signals. In current evidence, that is much more likely to land near the best quality–cost frontier than defaulting to heavy semantic or LLM-based chunking everywhere. citeturn32view0turn33view1turn29view0turn15view1turn24view0

For retrieval, prefer **precise chunks plus sentence-window or parent/child recovery** over “always overlap.” That keeps your formation phase cleaner, your indexes smaller, and your chunk semantics easier to reason about. citeturn14view1turn29view1turn33view1

For code, do **not** use line windows as your default. Use **AST-aware chunking** driven by Tree-sitter-class parsers, with recursive split-and-merge similar to cAST. If you want a CLI-native boundary today, ast-grep is a practical observation tool and Tree-sitter is the parsing substrate. citeturn37view0turn22view0turn13search0

Reserve **late chunking** for offline batch indexing where you can afford longer embedding passes and where cross-chunk contextual dependencies are clearly hurting retrieval. Reserve **LLM-driven chunking** for premium or specialized builds, not the baseline path on constrained local hardware. Treat **chunk-free retrieval** as important research context, but not the main engineering target unless the whole retrieval architecture is being redesigned around long-context hidden-state retrieval. citeturn34view0turn35view0turn35view1turn36view0turn33view2

### Open questions and limitations

The strongest broad performance result here comes from a 2026 arXiv benchmark rather than a finalized conference version, so it should be treated as high-value but still evolving evidence. citeturn32view0

The frontier methods with the most conceptual elegance in EBA terms—late chunking, LLM-guided chunking, and chunk-free retrieval—are not yet the best default fit for a strict CPU-only, local CLI pipeline. They matter, but today they are better treated as specialized formation operators than as the center of the architecture. citeturn34view0turn35view1turn36view0turn36view1

The research also reinforces that chunking is **domain-dependent**. Legal, mathematical, scientific, and code corpora do not want the same native unit. In EBA language: the system’s actual invariants are discovered per source family, not imposed globally. citeturn32view0turn37view0