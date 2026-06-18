from catalyst.shared.ids import (
    STABLE_ID_ALGORITHM_VERSION,
    STABLE_ID_HASH_ALGORITHM,
    stable_id,
    stable_id_metadata,
)


def test_stable_id_algorithm_metadata_is_explicit() -> None:
    metadata = stable_id_metadata()

    assert metadata["algorithm_version"] == STABLE_ID_ALGORITHM_VERSION
    assert metadata["hash_algorithm"] == STABLE_ID_HASH_ALGORITHM
    assert metadata["part_separator"] == "\\x1f"
    assert metadata["default_size"] == 16


def test_stable_id_generation_remains_deterministic() -> None:
    first = stable_id("src", "markdown", "hash")
    second = stable_id("src", "markdown", "hash")

    assert first == second
    assert first.startswith("src_")
    assert len(first.removeprefix("src_")) == 16
