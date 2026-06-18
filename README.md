# Catalyst Chunker

Catalyst is an invariant-first chunk formation package. It preserves source identity, observes document structure, evaluates invariants, forms chunk candidates, admits an auditable chunk graph, and emits versioned projections for retrieval and inspection.

The package is intended for two uses:

- standalone CLI: `catalyst chunk ./document.md --out chunks.jsonl --audit audit.json`
- internal library: import Catalyst operations from `catalyst.operation.commands`

Catalyst does not start from generic splitter behavior. The default path is source-preserving, structure-first, and audit-native.

## Current Build Scope

This initial implementation supports a local Markdown/plain-text path:

```text
SourceRecord
  -> markdown / paragraph / sentence / tokenizer observations
  -> source lineage and token budget invariants
  -> paragraph-group chunk candidates
  -> admitted ChunkGraph
  -> retrieval and audit projections
```

Later phases admit Docling, AST parsers, semantic refinement, hierarchical projections, and specialized retrieval modes behind explicit boundary ports and ADR constraints.

## Install For Development

```bash
python -m pip install -e ".[dev]"
pytest
```

## CLI

```bash
catalyst chunk ./docs/example.md --out ./out/chunks.jsonl --audit ./out/audit.json
catalyst inspect-boundaries ./docs/example.md --out ./out/boundaries.json
```

Every public output includes `schema_version` and `projection_kind`.
