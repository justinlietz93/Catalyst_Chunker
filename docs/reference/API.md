# API Reference

This page names the intended public Python surfaces for the pre-1.0 package.

## Package Version

```python
from catalyst import __version__
```

## Operations

Primary import path:

```python
from catalyst.operation.commands import (
    chunk_source,
    chunk_observed_source,
    chunk_parsed_code,
    emit_projection,
    emit_boundary_inspection,
    evaluate_candidates,
    evaluate_context_recovery,
    evaluate_retrieval_sanity,
    inspect_boundaries,
)
```

Result types:

```python
from catalyst.operation.commands import (
    CandidateEvaluation,
    ChunkCodeResult,
    ChunkSourceResult,
    ContextRecoveryBenchmark,
    RetrievalSanityEvaluation,
)
```

## Source Records

```python
from catalyst.source.records.source_record import SourceRecord
from catalyst.source.records.source_span import SourceSpan
```

## Observation Evidence

```python
from catalyst.observation.instruments.collect import observe_source
```

The default observation set includes `source_measure`, which reports raw source size measures such as character count, byte count, line count, lexical token count, and max atomic run length.

## Policy

```python
from catalyst.formation.selection.selection_policy import SelectionPolicy
```

## Boundary Ports

```python
from catalyst.boundary.ports import (
    ArtifactWriter,
    AstParserPort,
    DocumentParserPort,
    EmbeddingPort,
    LlmCandidatePort,
    ProviderTokenPort,
    SourceLoader,
    TelemetrySink,
    TokenizerPort,
)
```

## Boundary Adapters

Concrete adapters are public at the boundary layer:

```python
from catalyst.boundary.adapters.ast_python import PythonAstParser
from catalyst.boundary.adapters.tokenizers import ExampleProviderTokenizer
from catalyst.boundary.adapters.filesystem.source_loader import FileSystemSourceLoader
from catalyst.boundary.adapters.jsonl.artifact_writer import JsonlArtifactWriter
```

Optional adapters may require extras.

## Stability

Catalyst is pre-1.0. Public API changes should be documented in `CHANGELOG.md`. Internal modules may change without compatibility guarantees.

## Errors

```python
from catalyst.shared.errors import EmptySourceError, InvariantViolation
from catalyst.formation.selection import SelectionFailure
```

- `EmptySourceError`: source material contains no chunkable text.
- `SelectionFailure`: no candidate set satisfied selection policy; rejection records are attached to the error.
- `InvariantViolation`: admitted structures failed hard invariants.

See [Error Records](ERRORS.md) for the structured error shape.
