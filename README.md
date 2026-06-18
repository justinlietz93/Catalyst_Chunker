![alt text](https://raw.githubusercontent.com/justinlietz93/Catalyst_Chunker/main/docs/catalyst_chunker_banner.png)

**Catalyst Chunker** is an invariant-first chunk formation package for retrieval, agentic software, and document/code workflows that need source lineage and auditability.

Catalyst does not treat splitter output, parser output, embeddings, or LLM proposals as source truth. External tools may provide evidence, but accepted chunks are admitted only after Catalyst-native formation, invariant checks, and versioned projection.

## Status

`0.1.2` is an alpha release candidate. The package builds as a wheel, exposes a CLI, and passes the local release acceptance suite. Public APIs are usable, but schema and operation names should still be treated as pre-1.0.

The current release gate covers:

- immutable source records, spans, normalization traces, and lineage
- structure-first prose chunking for Markdown/plain text
- recursive fallback only after structural candidate failure
- AST-aware Python code chunking
- Docling, ast-grep, tokenizer, embedding, and LLM candidate ports/adapters behind boundary contracts
- optional semantic refinement as evidence, not authority
- parent/child and sentence-window context recovery projections
- rejected candidate, repair, fallback, and invariant audit records
- retrieval sanity and relation-context benchmark operations
- governance checks for layer direction, boundary purity, native naming, file size, projection schema fields, and release acceptance

## Install

From a local checkout:

```bash
python -m pip install -e ".[dev]"
```

After publication:

```bash
python -m pip install catalyst-chunker
```

Optional extras:

```bash
python -m pip install "catalyst-chunker[docling]"
python -m pip install "catalyst-chunker[ast-grep]"
python -m pip install "catalyst-chunker[sentence-transformers]"
```

The default package has no required runtime dependencies outside the Python standard library.

## CLI

```bash
catalyst --version
catalyst chunk ./document.md --out ./chunks.jsonl --audit ./audit.json
catalyst inspect-boundaries ./document.md --out ./boundaries.json
catalyst compare-strategies ./document.md --out ./candidate-evaluation.json
catalyst explain-chunk ./chunks.jsonl chk_...
catalyst audit ./audit.json
catalyst retrieval-sanity ./tests/fixtures/retrieval_sanity/heldout_fixtures.json --out ./retrieval-sanity.json
```

Every public output includes `schema_version` and `projection_kind`.

## Library Use

```python
from catalyst.operation.commands import chunk_source, emit_projection

result = chunk_source(b"# Title\n\nBody text for retrieval.")
retrieval_records = emit_projection(result, "retrieval")
audit_record = emit_projection(result, "audit")

assert result.invariant_ledger.passed
assert retrieval_records[0]["schema_version"] == "catalyst.retrieval.v1"
assert audit_record["projection_kind"] == "audit"
```

Python code chunking uses an AST parser boundary adapter:

```python
from catalyst.boundary.adapters.ast_python import PythonAstParser
from catalyst.operation.commands import chunk_parsed_code
from catalyst.projection.views.code_view import CodeProjection
from catalyst.source.records.source_record import SourceRecord

source = SourceRecord.from_bytes(
    b"def helper():\n    return 1\n",
    source_kind="code",
)
parsed = PythonAstParser().parse(source, "python")
result = chunk_parsed_code(parsed)
code_projection = CodeProjection(result.graph, parsed).record()
```

## Agentic And Ollama Use

Catalyst is designed to sit inside an agentic application as a source-preserving internal utility. The recommended pattern is:

1. Use Catalyst to admit chunks and emit retrieval/audit projections.
2. Give the agent retrieval records plus source spans, warnings, and relation context.
3. Keep model suggestions, including Ollama proposals, as boundary-assisted evidence.
4. Require audit output for prompt ID, policy ID, model identity, confidence, and rejected alternatives.

Tiny Ollama models such as OpenBMB MiniCPM variants can be useful for boundary-assisted candidate hints, summaries, or local reranking. Catalyst should still receive those outputs through `LlmCandidatePort` or another boundary adapter. The model output can influence evidence; it does not become an accepted chunk by authority.

Minimal boundary-assisted evidence example:

```python
from catalyst.observation.evidence import EvidenceSet, LlmCandidateObservation
from catalyst.observation.instruments.collect import observe_source
from catalyst.operation.commands import chunk_observed_source, emit_projection
from catalyst.source.records.source_record import SourceRecord

source = SourceRecord.from_bytes(b"Boundary-assisted candidate source.")
base_evidence = observe_source(source)
llm_evidence = LlmCandidateObservation(
    span=source.full_span(),
    proposal_text="candidate source",
    prompt_id="prompt_001",
    policy_id="local_ollama_boundary_assist",
    model_identity="ollama:<model-name>",
    confidence=0.72,
    rejected_alternatives=("too broad",),
).to_observation(source)

result = chunk_observed_source(
    source,
    EvidenceSet(base_evidence.source_id, (*base_evidence.observations, llm_evidence)),
)
audit = emit_projection(result, "audit")
```

In this pattern the agent can inspect `audit["evidence"]["boundary_assisted"]` to see which model contributed evidence and which alternatives were rejected.

## Projection Schemas

Current public projection kinds:

| Projection | Schema version |
|---|---|
| retrieval | `catalyst.retrieval.v1` |
| audit | `catalyst.audit.v1` |
| boundary inspection | `catalyst.boundaries.v1` |
| candidate evaluation | `catalyst.candidate_evaluation.v1` |
| retrieval sanity | `catalyst.retrieval_sanity.v1` |
| context recovery benchmark | `catalyst.context_recovery_benchmark.v1` |
| parent/child | `catalyst.parent_child.v1` |
| sentence window | `catalyst.sentence_window.v1` |
| code | `catalyst.code.v1` |
| specialized mode admission | `catalyst.specialized_mode_admission.v1` |

See [Projection Schemas](docs/reference/PROJECTIONS.md) for compatibility rules.

## Architecture Guarantees

Catalyst follows the ADR spine in `ADRs/` and the applied layer map in [Architecture](docs/architecture/ARCHITECTURE.md).

Core guarantees:

- source identity and source spans are mandatory
- accepted chunks preserve lineage
- fixed-size slicing is fallback-only and audit-visible
- semantic/LLM evidence cannot override source, structure, or hard invariants
- rejected candidates remain inspectable
- boundary adapters cannot be imported inward
- public records are schema-versioned

## Development

Documentation starts at [docs/README.md](docs/README.md). Contributor setup and verification details live in [Contributing](docs/development/CONTRIBUTING.md) and [Testing](docs/development/TESTING.md).

```bash
python -m pip install -e ".[dev]"
python -m pytest
python governance/tools/enforce_file_size.py
python governance/tools/enforce_native_names.py
python governance/tools/enforce_boundary_purity.py
lint-imports --config .importlinter
python -m compileall -q src tests governance/tools
python -m pip wheel . --no-deps -w dist
```

The CI workflow runs the same gates.

## Documentation

- [Quickstart](docs/guides/QUICKSTART.md)
- [CLI Guide](docs/guides/CLI.md)
- [Library Usage](docs/guides/LIBRARY_USAGE.md)
- [Agentic Integration](docs/guides/AGENTIC_INTEGRATION.md)
- [API Reference](docs/reference/API.md)
- [Configuration](docs/reference/CONFIGURATION.md)
- [Architecture](docs/architecture/ARCHITECTURE.md)

## Release

Build and check release artifacts:

```bash
python -m build
twine check dist/*
```

Publish to TestPyPI first:

```bash
twine upload --repository testpypi dist/*
```

Then publish to PyPI:

```bash
twine upload dist/*
```

Before publishing, review `RELEASE_CHECKLIST.md` and [Release](docs/development/RELEASE.md).

## License

MIT. See `LICENSE`.
