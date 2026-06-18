"""Filesystem source loading adapter."""

from __future__ import annotations

from pathlib import Path


class FileSystemSourceLoader:
    """Load source bytes from the local filesystem."""

    def load(self, location: str) -> bytes:
        return Path(location).read_bytes()
