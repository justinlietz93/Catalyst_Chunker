# Quickstart

This guide gets a local Catalyst install running against one Markdown file.

## Install

For a local checkout:

```bash
python -m pip install -e ".[dev]"
```

After publication:

```bash
python -m pip install catalyst-chunker
```

Verify the CLI:

```bash
catalyst --version
```

## Chunk A Markdown File

Create a small document:

```bash
printf '# Title\n\nBody text for retrieval.\n' > /tmp/catalyst-example.md
```

Emit retrieval records and an audit record:

```bash
catalyst chunk /tmp/catalyst-example.md \
  --out /tmp/catalyst-chunks.jsonl \
  --audit /tmp/catalyst-audit.json
```

Inspect the first retrieval record:

```bash
head -n 1 /tmp/catalyst-chunks.jsonl
```

Inspect the audit summary:

```bash
catalyst audit /tmp/catalyst-audit.json
```

## Use From Python

```python
from catalyst.operation.commands import chunk_source, emit_projection

result = chunk_source(b"# Title\n\nBody text for retrieval.")
retrieval = emit_projection(result, "retrieval")
audit = emit_projection(result, "audit")

assert result.invariant_ledger.passed
assert retrieval[0]["projection_kind"] == "retrieval"
assert audit["projection_kind"] == "audit"
```

## What To Expect

Catalyst produces admitted chunks with source spans, evidence IDs, warnings, and versioned projection records. It does not require embeddings or LLMs for the default path.
