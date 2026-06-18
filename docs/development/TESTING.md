# Testing

Catalyst uses tests and governance scripts as release gates.

## Full Verification

```bash
python -m pytest
python governance/tools/enforce_file_size.py
python governance/tools/enforce_native_names.py
python governance/tools/enforce_boundary_purity.py
lint-imports --config .importlinter
python -m compileall -q src tests governance/tools
python -m build
twine check dist/*
```

## Test Groups

- `tests/unit`: small behavior and invariant checks.
- `tests/contract`: boundary port and adapter contracts.
- `tests/contradiction`: fixtures that must not be accepted silently.
- `tests/integration`: multi-layer behavior.
- `tests/e2e`: CLI and release acceptance gates.
- `tests/fixtures/benchmarks`: admitted-strategy, context-recovery, and golden retrieval corpus fixtures.

## Governance Scripts

- `enforce_file_size.py`: keeps files within the project size rule.
- `enforce_native_names.py`: rejects unearned generic architecture names.
- `enforce_boundary_purity.py`: prevents concrete boundary adapters from being imported inward.

## Import Contracts

```bash
lint-imports --config .importlinter
```

Import-linter enforces EBA layer direction and boundary purity.
