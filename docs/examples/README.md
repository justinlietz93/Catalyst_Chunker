# Examples

These examples are intentionally small and can be copied into a local shell or Python session.

## CLI Chunking

```bash
printf '# Example\n\nA paragraph for retrieval.\n' > /tmp/catalyst-example.md
catalyst chunk /tmp/catalyst-example.md \
  --out /tmp/catalyst-chunks.jsonl \
  --audit /tmp/catalyst-audit.json
catalyst audit /tmp/catalyst-audit.json
```

## Library Chunking

```python
from catalyst.operation.commands import chunk_source, emit_projection

result = chunk_source(b"# Example\n\nA paragraph for retrieval.")
retrieval = emit_projection(result, "retrieval")
print(retrieval[0]["chunk_id"])
```

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
print(len(result.graph.chunks))
```

## Context Recovery Benchmark

```python
from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.operation.commands import evaluate_context_recovery

record = evaluate_context_recovery(
    b"Catalyst names source identity.\n\nLineage remains inspectable.",
    expected_terms=("catalyst", "lineage"),
    policy=SelectionPolicy(target_tokens=2, hard_max_tokens=20),
).record()
print(record["retrieval_quality"])
```

## Provider Token Budget Estimate

```python
from catalyst.boundary.adapters.tokenizers import ExampleProviderTokenizer

tokenizer = ExampleProviderTokenizer(
    provider="ollama",
    model_identity="ollama:tiny",
    characters_per_token=4,
)
measure = tokenizer.measure("source text for a model")
print(measure.to_dict())
```

## Generic Retrieval Ingestion

See [retrieval_ingestion.py](retrieval_ingestion.py) for an app-neutral mapping from Catalyst retrieval projection records into ingestion records.
