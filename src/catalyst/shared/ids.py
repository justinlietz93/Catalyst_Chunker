"""Deterministic identifiers and hashes."""

from __future__ import annotations

from hashlib import sha256

STABLE_ID_ALGORITHM_VERSION = "catalyst.stable_id.v1"
STABLE_ID_HASH_ALGORITHM = "sha256"
STABLE_ID_SEPARATOR = "\x1f"
STABLE_ID_DEFAULT_SIZE = 16


def content_hash(value: bytes | str) -> str:
    """Return a SHA-256 hex digest for bytes or text."""

    data = value.encode("utf-8") if isinstance(value, str) else value
    return sha256(data).hexdigest()


def stable_id(prefix: str, *parts: object, size: int = 16) -> str:
    """Create a deterministic compact ID from stable parts."""

    joined = STABLE_ID_SEPARATOR.join(str(part) for part in parts)
    return f"{prefix}_{content_hash(joined)[:size]}"


def stable_id_metadata() -> dict[str, object]:
    """Describe the current stable ID algorithm for docs and diagnostics."""

    return {
        "algorithm_version": STABLE_ID_ALGORITHM_VERSION,
        "hash_algorithm": STABLE_ID_HASH_ALGORITHM,
        "part_separator": "\\x1f",
        "default_size": STABLE_ID_DEFAULT_SIZE,
    }
