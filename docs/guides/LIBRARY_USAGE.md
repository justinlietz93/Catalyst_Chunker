# Library Usage

Catalyst can be embedded as an internal utility in retrieval and agentic applications.

## Public Operation Imports

Use `catalyst.operation.commands` as the main public surface:

```python
from catalyst.operation.commands import (
    chunk_source,
    chunk_observed_source,
    chunk_parsed_code,
    emit_projection,
    evaluate_candidates,
    evaluate_context_recovery,
    evaluate_retrieval_sanity,
    inspect_boundaries,
)
```

These names are pre-1.0 public APIs. They are usable, but may change with explicit changelog entries.

## Default Prose Chunking

```python
from catalyst.operation.commands import chunk_source, emit_projection

result = chunk_source(b"# Heading\n\nA paragraph for retrieval.")
records = emit_projection(result, "retrieval")
audit = emit_projection(result, "audit")
```

The result contains:

- `source`: immutable source record.
- `evidence`: observations made over the source.
- `selection`: accepted and rejected candidate information.
- `graph`: admitted chunk graph.
- `invariant_ledger`: invariant results.

## Policy Control

```python
from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.operation.commands import chunk_source

policy = SelectionPolicy(target_tokens=300, hard_max_tokens=500)
result = chunk_source(b"# Title\n\nBody.", policy=policy)
```

Policy fields are documented in [Configuration](../reference/CONFIGURATION.md).

The default token counter is whitespace-delimited. For provider-specific model budgets, map the provider's token budget conservatively before creating a `SelectionPolicy`, or provide tokenizer evidence through a boundary adapter.

## Code Chunking

```python
from catalyst.boundary.adapters.ast_python import PythonAstParser
from catalyst.operation.commands import chunk_parsed_code
from catalyst.source.records.source_record import SourceRecord

source = SourceRecord.from_bytes(
    b"def helper():\n    return 1\n",
    source_kind="code",
)
parsed = PythonAstParser().parse(source, "python")
result = chunk_parsed_code(parsed)
```

The concrete parser is a boundary adapter. Internal formation receives Catalyst-native parsed code records.

## Projection Selection

```python
retrieval = emit_projection(result, "retrieval")
audit = emit_projection(result, "audit")
parent_child = emit_projection(result, "parent_child")
sentence_window = emit_projection(result, "sentence_window")
```

Projection fields are versioned public records. See [Projection Schemas](../reference/PROJECTIONS.md).

## Retrieval Sanity Evaluation

```python
from catalyst.operation.commands import evaluate_retrieval_sanity

report = evaluate_retrieval_sanity((fixture,)).record()
metrics = report["fixtures"][0]["strategy_results"][0]["retrieval_metrics"]
```

Retrieval sanity fixtures can declare query text, expected answer terms, and relevant source spans. Catalyst ranks candidate chunks with a deterministic lexical baseline and reports recall/MRR as diagnostic evidence only.

## Empty Sources

Empty, whitespace-only, and newline-only sources raise `EmptySourceError`.

```python
from catalyst.operation.commands import chunk_source
from catalyst.shared.errors import EmptySourceError

try:
    chunk_source(b"\n\n")
except EmptySourceError:
    pass
```
