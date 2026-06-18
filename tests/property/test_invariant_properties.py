from __future__ import annotations

from typing import Any

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from catalyst.formation.selection.selection_policy import SelectionPolicy
from catalyst.invariant.checks.offset_reversibility_check import check_offset_reversibility
from catalyst.invariant.checks.source_coverage_check import check_source_coverage
from catalyst.invariant.checks.source_lineage_check import check_source_lineage
from catalyst.invariant.checks.token_budget_check import check_token_budget
from catalyst.observation.instruments.tokenizer_instrument import count_tokens
from catalyst.operation.commands.chunk_source import chunk_source
from catalyst.shared.errors import EmptySourceError
from catalyst.shared.ids import STABLE_ID_DEFAULT_SIZE, stable_id


PROPERTY_SETTINGS = settings(
    max_examples=60,
    deadline=None,
    suppress_health_check=(HealthCheck.too_slow,),
)

TOKEN_ALPHABET = tuple(
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    ".,;:!?-_/#"
    "áéíóúñβλ漢字かな🙂"
)
WHITESPACE_ALPHABET = (" ", "\t", "\n", "\r")


stable_part_strategy = st.one_of(
    st.text(alphabet=TOKEN_ALPHABET + WHITESPACE_ALPHABET, min_size=0, max_size=24),
    st.integers(min_value=-10_000, max_value=10_000),
    st.booleans(),
    st.none(),
)

token_strategy = st.text(alphabet=TOKEN_ALPHABET, min_size=1, max_size=12)


@st.composite
def _document_text(draw: st.DrawFn) -> str:
    paragraph_count = draw(st.integers(min_value=1, max_value=4))
    paragraphs: list[str] = []
    for _ in range(paragraph_count):
        token_count = draw(st.integers(min_value=1, max_value=40))
        tokens = draw(st.lists(token_strategy, min_size=token_count, max_size=token_count))
        separators = draw(
            st.lists(
                st.sampled_from((" ", "  ", "\t", "\n")),
                min_size=max(token_count - 1, 0),
                max_size=max(token_count - 1, 0),
            )
        )
        paragraph = "".join(
            token + (separators[index] if index < len(separators) else "")
            for index, token in enumerate(tokens)
        )
        paragraphs.append(paragraph)
    return "\n\n".join(paragraphs)


@PROPERTY_SETTINGS
@given(
    prefix=st.text(alphabet=tuple("abcdefghijklmnopqrstuvwxyz"), min_size=1, max_size=8),
    parts=st.lists(stable_part_strategy, min_size=0, max_size=6),
)
def test_stable_id_is_deterministic_for_generated_parts(
    prefix: str,
    parts: list[Any],
) -> None:
    first = stable_id(prefix, *parts)
    second = stable_id(prefix, *parts)

    assert first == second
    assert first.startswith(f"{prefix}_")
    assert len(first.removeprefix(f"{prefix}_")) == STABLE_ID_DEFAULT_SIZE


@PROPERTY_SETTINGS
@given(text=_document_text())
def test_generated_documents_preserve_core_invariants(text: str) -> None:
    policy = SelectionPolicy(target_tokens=8, hard_max_tokens=13)

    result = chunk_source(text.encode("utf-8"), policy=policy)
    chunks = result.graph.chunks
    paragraph_spans = tuple(observation.span for observation in result.evidence.by_kind("paragraph"))
    chunk_spans = tuple(span for chunk in chunks for span in chunk.spans)

    assert chunks
    assert result.invariant_ledger.passed
    assert check_source_coverage(required_spans=paragraph_spans, chunks=chunks).passed
    assert check_source_lineage(chunks).passed
    assert check_offset_reversibility(result.source, chunk_spans).passed
    assert check_token_budget(chunks, policy.hard_max_tokens).passed

    for chunk in chunks:
        assert chunk.source_id == result.source.source_id
        assert chunk.spans
        assert chunk.token_count == count_tokens(chunk.text)
        for span in chunk.spans:
            assert span.source_id == result.source.source_id
            assert 0 <= span.start_char <= span.end_char <= len(result.source.canonical_text)
            assert span.start_byte == len(result.source.canonical_text[: span.start_char].encode("utf-8"))
            assert span.end_byte == len(result.source.canonical_text[: span.end_char].encode("utf-8"))


@PROPERTY_SETTINGS
@given(tokens=st.lists(token_strategy, min_size=1, max_size=64))
def test_whitespace_token_budget_holds_for_generated_token_runs(tokens: list[str]) -> None:
    hard_max = 7
    text = " ".join(tokens)
    result = chunk_source(
        text.encode("utf-8"),
        policy=SelectionPolicy(target_tokens=5, hard_max_tokens=hard_max),
    )

    assert result.invariant_ledger.passed
    assert all(chunk.token_count <= hard_max for chunk in result.graph.chunks)
    assert sum(chunk.token_count for chunk in result.graph.chunks) == len(tokens)
    assert 1 <= len(result.graph.chunks) <= len(tokens)


@PROPERTY_SETTINGS
@given(text=st.text(alphabet=WHITESPACE_ALPHABET, min_size=0, max_size=80))
def test_empty_like_generated_sources_raise_typed_error(text: str) -> None:
    with pytest.raises(EmptySourceError) as captured:
        chunk_source(text.encode("utf-8"))

    record = captured.value.to_dict()
    assert record["code"] == "source.empty"
    assert record["details"]["character_count"] == len(text)


@PROPERTY_SETTINGS
@given(token=st.text(alphabet=TOKEN_ALPHABET, min_size=20, max_size=160))
def test_long_atomic_generated_token_remains_one_baseline_token(token: str) -> None:
    result = chunk_source(
        token.encode("utf-8"),
        policy=SelectionPolicy(target_tokens=1, hard_max_tokens=1),
    )

    assert result.invariant_ledger.passed
    assert len(result.graph.chunks) == 1
    assert result.graph.chunks[0].token_count == 1
    assert result.graph.chunks[0].text == token
