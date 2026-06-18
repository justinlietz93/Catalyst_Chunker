# Retrieval Ingestion

Catalyst's authoritative retrieval output is the versioned retrieval projection. Applications can map those records into their own ingestion shape without making their storage or ranking system part of Catalyst core.

## Generic Mapping

The app-neutral example lives at [retrieval_ingestion.py](../examples/retrieval_ingestion.py).

It carries:

- `projection_schema_version`
- `source_projection_kind`
- `chunk_id`
- `source_id`
- `indexed_text`
- `source_spans`
- `relation_references`
- `metadata`

The example intentionally avoids vector database fields, provider DTOs, and downstream application names.

## Usage

```python
from catalyst.operation.commands import chunk_source, emit_projection

# after copying docs/examples/retrieval_ingestion.py into your app:
from retrieval_ingestion import retrieval_records_to_ingestion_records

result = chunk_source(b"# Title\n\nBody text for retrieval.")
retrieval = emit_projection(result, "retrieval")
records = retrieval_records_to_ingestion_records(retrieval)
```

Application adapters should apply embedding, provider-token, ranking, and storage-specific mappings after this point.

## Boundary Rule

If a consumer needs a different ingestion DTO, build it in that consuming application. Catalyst should expose source-preserving projections and examples, not become a vector database adapter layer.
