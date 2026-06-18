# Changelog

All notable changes to Catalyst Chunker are recorded here.

## 0.1.7 - Unreleased

### Added

- Diagnostic performance benchmark operation, CLI command, fixtures, and projection schema with elapsed time, peak memory, source measures, chunk/token counts, repair counts, strategy identity, and invariant summaries.

## 0.1.6 - Unreleased

### Added

- Held-out retrieval sanity metrics with deterministic lexical ranking, recall@k, MRR, relevant candidate IDs, and fixture-declared relevant source spans.

## 0.1.5 - Unreleased

### Added

- Bounded property-based invariant fuzzing for stable IDs, source-span reversibility, source coverage, source lineage, whitespace-token budgets, empty-like sources, and long atomic-token behavior.

## 0.1.4 - Unreleased

### Added

- Stable ID algorithm constants and documentation.
- Structured Catalyst error records for caller-facing failure handling.
- Provider-token boundary example for downstream model-token budget mapping.
- Golden retrieval benchmark corpus fixture for regression-oriented evaluation work.
- Roadmap and ADRs for invariant, retrieval, benchmark, ingestion, and telemetry priorities.

## 0.1.3 - 2026-06-18

Initial alpha release candidate.

### Added

- Source identity, spans, lineage maps, reversible normalization, and provenance records.
- Observation evidence sets for Markdown, paragraphs, sentences, lists, tables, PDF layout, code AST, tokenizer evidence, semantic shifts, and LLM boundary assistance.
- Invariant ledger and checks for coverage, lineage, offset reversibility, token budget honesty, fallback evidence, rejection visibility, and projection schema versioning.
- Structure-first prose chunking, recursive fallback, hierarchical candidates, AST code candidates, and semantic refinement candidates.
- Accepted chunk graphs with typed relation kinds.
- Retrieval, audit, boundary inspection, candidate evaluation, retrieval sanity, parent/child, sentence-window, code, context-recovery benchmark, and specialized-mode projections.
- CLI commands for chunking, boundary inspection, strategy comparison, chunk explanation, audit summary, and retrieval sanity evaluation.
- Boundary ports and adapters for filesystem loading, JSONL writing, tokenizers, Docling, Python AST, ast-grep, embeddings, telemetry, and LLM candidate proposals.
- Governance checks for architecture direction, native naming, boundary purity, file size, and release acceptance.
- Public documentation tree under `docs/` with guides, reference pages, development notes, and examples.
- Typed `EmptySourceError` for empty or whitespace-only sources.
- Documentation for baseline token-budget semantics and provider-token adapter responsibilities.
- `source_measure` observation with character, byte, line, lexical-token, and max-atomic-run counts.

### Notes

- Public APIs and schema versions are pre-1.0 and may change with explicit changelog entries.
- Ollama and other LLM systems are intended to connect through boundary ports; no concrete Ollama adapter is bundled in this release.
