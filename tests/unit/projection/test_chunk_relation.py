import pytest

from catalyst.projection.chunks.chunk_relation import ChunkRelation


def test_chunk_relation_rejects_unknown_relation_kind() -> None:
    with pytest.raises(ValueError):
        ChunkRelation("a", "b", "mystery")
