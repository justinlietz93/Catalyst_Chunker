"""Sentence Transformers embedding boundary adapter."""

from __future__ import annotations

from typing import Any

from catalyst.shared.errors import CatalystError


class SentenceTransformersEmbeddingAdapter:
    """Return embeddings from a Sentence Transformers model."""

    def __init__(
        self,
        *,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        model: Any | None = None,
        normalize: bool = True,
    ) -> None:
        self.model_name = model_name
        self.model_identity = f"sentence-transformers:{model_name}"
        self._model = model
        self._normalize = normalize

    def embed(self, texts: tuple[str, ...]) -> tuple[tuple[float, ...], ...]:
        if not texts:
            return ()
        raw_embeddings = self._model_instance().encode(
            list(texts),
            normalize_embeddings=self._normalize,
        )
        return tuple(_as_float_tuple(item) for item in raw_embeddings)

    def _model_instance(self) -> Any:
        if self._model is not None:
            return self._model
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise CatalystError(
                "SentenceTransformersEmbeddingAdapter requires the optional dependency: "
                "catalyst-chunker[sentence-transformers]"
            ) from exc
        self._model = SentenceTransformer(self.model_name)
        return self._model


def _as_float_tuple(value: Any) -> tuple[float, ...]:
    if hasattr(value, "tolist"):
        value = value.tolist()
    return tuple(float(item) for item in value)
