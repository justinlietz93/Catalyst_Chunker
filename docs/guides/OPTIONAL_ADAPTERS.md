# Optional Adapters

The default package has no required runtime dependencies outside the Python standard library.

Optional integrations are installed through extras or implemented by callers behind ports.

## Docling

```bash
python -m pip install "catalyst-chunker[docling]"
```

Docling remains a boundary adapter. Its parsed document output must be translated into Catalyst-native records before internal operations use it.

## ast-grep

```bash
python -m pip install "catalyst-chunker[ast-grep]"
```

The ast-grep adapter is a code observation boundary. AST evidence supports candidate formation, but provider objects do not flow inward.

## Sentence Transformers

```bash
python -m pip install "catalyst-chunker[sentence-transformers]"
```

Embeddings are optional evidence for semantic refinement. They do not become source truth.

## LLM Providers

No LLM provider is bundled. Applications can implement `LlmCandidatePort` for Ollama, OpenAI-compatible local servers, or other systems.

LLM proposals should be recorded as boundary-assisted evidence and audited.

## Provider Token Counters

Applications that need downstream model-token budgets can implement `ProviderTokenPort`.

Catalyst includes `ExampleProviderTokenizer` as a copyable boundary example:

```python
from catalyst.boundary.adapters.tokenizers import ExampleProviderTokenizer

tokenizer = ExampleProviderTokenizer(
    provider="ollama",
    model_identity="ollama:tiny",
    characters_per_token=4,
)
measure = tokenizer.measure("some source text")
```

Provider-token counts are boundary evidence for application policy decisions. They do not replace Catalyst's default source-preserving token observations by authority.
