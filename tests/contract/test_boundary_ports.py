import json

from catalyst.boundary.adapters.filesystem.source_loader import FileSystemSourceLoader
from catalyst.boundary.adapters.embeddings.sentence_transformers_embedding import (
    SentenceTransformersEmbeddingAdapter,
)
from catalyst.boundary.adapters.jsonl.artifact_writer import JsonlArtifactWriter
from catalyst.boundary.adapters.telemetry import (
    InMemoryTelemetrySink,
    NoOpTelemetrySink,
    record_telemetry,
)
from catalyst.boundary.adapters.tokenizers.provider_token_example import ExampleProviderTokenizer
from catalyst.boundary.adapters.tokenizers.whitespace_tokenizer import WhitespaceTokenizer
from catalyst.boundary.ports.artifact_writer import ArtifactWriter
from catalyst.boundary.ports.embedding_port import EmbeddingPort
from catalyst.boundary.ports.llm_candidate_port import (
    LlmCandidatePort,
    LlmCandidatePrompt,
    LlmCandidateProposal,
)
from catalyst.boundary.ports.source_loader import SourceLoader
from catalyst.boundary.ports.telemetry_events import (
    CHUNK_SOURCE_COMPLETED,
    TELEMETRY_EVENT_NAMES,
    TELEMETRY_EVENT_PAYLOAD_FIELDS,
    telemetry_payload_fields,
)
from catalyst.boundary.ports.telemetry_sink import TelemetrySink
from catalyst.boundary.ports.tokenizer_port import TokenizerPort
from catalyst.boundary.ports.provider_token_port import ProviderTokenPort


def test_filesystem_loader_satisfies_source_loader_port(tmp_path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("hello", encoding="utf-8")
    loader = FileSystemSourceLoader()

    assert isinstance(loader, SourceLoader)
    assert loader.load(str(source)) == b"hello"


def test_jsonl_writer_satisfies_artifact_writer_port(tmp_path) -> None:
    out = tmp_path / "records.jsonl"
    writer = JsonlArtifactWriter()

    assert isinstance(writer, ArtifactWriter)
    writer.write_records(str(out), ({"a": 1}, {"b": 2}))

    assert [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()] == [
        {"a": 1},
        {"b": 2},
    ]


def test_whitespace_tokenizer_satisfies_tokenizer_port() -> None:
    tokenizer = WhitespaceTokenizer()

    assert isinstance(tokenizer, TokenizerPort)
    assert tokenizer.count("one two three") == 3


def test_example_provider_tokenizer_satisfies_provider_token_port() -> None:
    tokenizer = ExampleProviderTokenizer(
        provider="ollama",
        model_identity="ollama:tiny",
        characters_per_token=4,
    )

    measure = tokenizer.measure("abcdefghi")

    assert isinstance(tokenizer, ProviderTokenPort)
    assert measure.token_count == 3
    assert measure.to_dict()["provider"] == "ollama"
    assert measure.to_dict()["model_identity"] == "ollama:tiny"


def test_embedding_adapter_shape_satisfies_embedding_port() -> None:
    adapter = _FixtureEmbeddingAdapter()

    assert isinstance(adapter, EmbeddingPort)
    assert adapter.embed(("a", "bb")) == ((1.0,), (2.0,))


def test_sentence_transformers_adapter_satisfies_embedding_port_with_injected_model() -> None:
    adapter = SentenceTransformersEmbeddingAdapter(model=_FixtureSentenceTransformer())

    assert isinstance(adapter, EmbeddingPort)
    assert adapter.embed(("a", "bb")) == ((1.0, 2.0), (2.0, 3.0))
    assert adapter.model_identity.startswith("sentence-transformers:")


def test_telemetry_sink_shape_satisfies_telemetry_port() -> None:
    sink = _FixtureTelemetrySink()

    assert isinstance(sink, TelemetrySink)
    sink.record("event", {"ok": True})
    assert sink.events == (("event", {"ok": True}),)


def test_noop_and_in_memory_telemetry_adapters_satisfy_telemetry_port() -> None:
    noop = NoOpTelemetrySink()
    memory = InMemoryTelemetrySink()
    payload = {"source_id": "src", "chunk_count": 1}

    assert isinstance(noop, TelemetrySink)
    assert isinstance(memory, TelemetrySink)
    assert record_telemetry(noop, CHUNK_SOURCE_COMPLETED, payload) is True
    assert record_telemetry(memory, CHUNK_SOURCE_COMPLETED, payload) is True
    payload["chunk_count"] = 2

    assert memory.events[0].event_name == CHUNK_SOURCE_COMPLETED
    assert memory.events[0].payload == {"source_id": "src", "chunk_count": 1}


def test_telemetry_recording_is_nonfatal_unless_strict() -> None:
    sink = _FailingTelemetrySink()

    assert record_telemetry(sink, CHUNK_SOURCE_COMPLETED, {}, strict=False) is False
    try:
        record_telemetry(sink, CHUNK_SOURCE_COMPLETED, {}, strict=True)
    except RuntimeError as error:
        assert "telemetry failed" in str(error)
    else:
        raise AssertionError("strict telemetry should re-raise sink failures")


def test_telemetry_event_payload_shapes_avoid_full_source_text() -> None:
    forbidden = {"text", "source_text", "indexed_text", "chunk_text", "raw_bytes"}

    assert CHUNK_SOURCE_COMPLETED in TELEMETRY_EVENT_NAMES
    assert telemetry_payload_fields(CHUNK_SOURCE_COMPLETED)
    for fields in TELEMETRY_EVENT_PAYLOAD_FIELDS.values():
        assert forbidden.isdisjoint(fields)


def test_llm_candidate_adapter_shape_satisfies_llm_candidate_port() -> None:
    adapter = _FixtureLlmCandidateAdapter()
    prompt = LlmCandidatePrompt(
        prompt_id="prompt_fixture",
        source_id="src",
        policy_id="policy_fixture",
        text="propose candidates",
    )

    proposals = adapter.propose(prompt)

    assert isinstance(adapter, LlmCandidatePort)
    assert proposals[0].model_identity == "fixture-llm"
    assert proposals[0].rejected_alternatives == ("too broad",)


class _FixtureEmbeddingAdapter:
    def embed(self, texts: tuple[str, ...]) -> tuple[tuple[float, ...], ...]:
        return tuple((float(len(text)),) for text in texts)


class _FixtureSentenceTransformer:
    def encode(self, texts, *, normalize_embeddings: bool):
        assert normalize_embeddings is True
        return [[float(len(text)), float(len(text) + 1)] for text in texts]


class _FixtureTelemetrySink:
    def __init__(self) -> None:
        self._events: list[tuple[str, dict[str, object]]] = []

    @property
    def events(self) -> tuple[tuple[str, dict[str, object]], ...]:
        return tuple(self._events)

    def record(self, event_name: str, payload: dict[str, object]) -> None:
        self._events.append((event_name, payload))


class _FailingTelemetrySink:
    def record(self, event_name: str, payload: dict[str, object]) -> None:
        raise RuntimeError("telemetry failed")


class _FixtureLlmCandidateAdapter:
    def propose(self, prompt: LlmCandidatePrompt) -> tuple[LlmCandidateProposal, ...]:
        return (
            LlmCandidateProposal(
                proposal_id=f"{prompt.prompt_id}_proposal",
                text="candidate text",
                model_identity="fixture-llm",
                confidence=0.71,
                rejected_alternatives=("too broad",),
            ),
        )
