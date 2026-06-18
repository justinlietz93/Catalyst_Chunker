# Catalyst Boundaries

Boundary code connects Catalyst to external tools and files. Boundary adapters translate provider output into Catalyst-native records before operation, formation, invariant, or projection logic uses it.

## Ports

- `SourceLoader`: load source bytes.
- `ArtifactWriter`: write projection records.
- `TokenizerPort`: count tokens.
- `DocumentParserPort`: parse documents into `ParsedDocument`.
- `AstParserPort`: parse code into `ParsedCode`.
- `EmbeddingPort`: return embedding vectors.
- `TelemetrySink`: record external telemetry.
- `LlmCandidatePort`: propose LLM-assisted candidate text.
- `ProviderTokenPort`: report downstream model-token counts as boundary evidence.

## Concrete Adapters

- filesystem source loader
- JSONL artifact writer
- whitespace tokenizer
- provider token example tokenizer
- Docling document parser
- Python AST parser
- ast-grep parser
- Sentence Transformers embedding adapter
- no-op and in-memory telemetry adapters
- CLI presentation

## Translation Rules

Adapters may import provider libraries and provider-shaped data. They must return Catalyst-native values such as `SourceRecord`, `EvidenceSet`, `ParsedDocument`, `ParsedCode`, or primitive records from boundary ports.

Provider chunks, LLM proposals, embeddings, and parser output are evidence. They do not become accepted chunks by provider authority.

Telemetry adapters record operational observations only. Telemetry failures are nonfatal by default and telemetry payloads should not include full source text.

## Error Translation

Boundary adapter failures should raise `CatalystError` with actionable messages. Optional dependency failures should name the extra needed to enable the adapter.

## Security Constraints

Adapters must not pull concrete provider objects into internal layers. Governance checks reject inward imports from `catalyst.boundary.adapters` and `catalyst.boundary.presentation`.
