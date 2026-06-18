"""Prevent concrete boundary adapter imports from internal layers."""

from __future__ import annotations

import ast
from pathlib import Path

INTERNAL_ROOTS = (
    Path("src/catalyst/source"),
    Path("src/catalyst/observation"),
    Path("src/catalyst/invariant"),
    Path("src/catalyst/formation"),
    Path("src/catalyst/operation"),
    Path("src/catalyst/projection"),
)
FORBIDDEN_PREFIXES = (
    "catalyst.boundary.adapters",
    "catalyst.boundary.presentation",
)


def main() -> int:
    failures: list[str] = []
    for root in INTERNAL_ROOTS:
        for path in root.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                module = _imported_module(node)
                if module and module.startswith(FORBIDDEN_PREFIXES):
                    failures.append(f"{path}: {module}")

    if failures:
        print("Concrete boundary imports found inside internal layers:")
        for failure in failures:
            print(f"  {failure}")
        return 1
    return 0


def _imported_module(node: ast.AST) -> str | None:
    if isinstance(node, ast.ImportFrom):
        return node.module
    if isinstance(node, ast.Import):
        return node.names[0].name if node.names else None
    return None


if __name__ == "__main__":
    raise SystemExit(main())
