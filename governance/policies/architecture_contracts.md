# Architecture Contracts

Catalyst follows ADR-0001 through ADR-0010 as accepted foundational decisions.

Current executable governance checks:

- `python3 governance/tools/enforce_file_size.py`
- `python3 governance/tools/enforce_native_names.py`
- `python3 governance/tools/enforce_boundary_purity.py`

These checks are intentionally narrow while the package is being admitted. They cover implementation and test files first; broader documentation gates can be added once the docs are split into the `docs/` structure described by `ARCHITECTURE_STANDARDS.md`.
