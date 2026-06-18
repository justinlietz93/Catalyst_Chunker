"""Reject vague architecture names unless an ADR admits them."""

from __future__ import annotations

from pathlib import Path

BANNED_FILE_PARTS = {
    "common",
    "controller",
    "helper",
    "manager",
    "misc",
    "pipeline",
    "processor",
    "repository",
    "service",
    "utils",
    "worker",
}


def main() -> int:
    failures: list[str] = []
    for path in Path("src").rglob("*.py"):
        parts = set(path.stem.lower().replace("-", "_").split("_"))
        if parts & BANNED_FILE_PARTS:
            failures.append(str(path))

    if failures:
        print("Vague architecture file names require an ADR:")
        for failure in failures:
            print(f"  {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
