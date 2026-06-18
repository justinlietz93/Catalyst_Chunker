"""Enforce focused source files."""

from __future__ import annotations

import argparse
from pathlib import Path

DEFAULT_ROOTS = ("src", "tests", "governance/tools")
DEFAULT_MAX_LINES = 500


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-lines", type=int, default=DEFAULT_MAX_LINES)
    parser.add_argument("roots", nargs="*", default=DEFAULT_ROOTS)
    args = parser.parse_args()

    failures: list[str] = []
    for root in args.roots:
        for path in Path(root).rglob("*"):
            if path.suffix not in {".py", ".md"} or not path.is_file():
                continue
            line_count = len(path.read_text(encoding="utf-8").splitlines())
            if line_count > args.max_lines:
                failures.append(f"{path}: {line_count} lines")

    if failures:
        print("Files exceed size policy:")
        for failure in failures:
            print(f"  {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
