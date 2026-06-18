# Release Checklist

Use this checklist before publishing `catalyst-chunker` to PyPI.

## Version

- [ ] Confirm `pyproject.toml` version.
- [ ] Confirm `src/catalyst/__init__.py` `__version__`.
- [ ] Confirm `CHANGELOG.md` release date and notes.
- [ ] Confirm README status language still matches the release.

## Verification

- [ ] `python -m pytest`
- [ ] `python governance/tools/enforce_file_size.py`
- [ ] `python governance/tools/enforce_native_names.py`
- [ ] `python governance/tools/enforce_boundary_purity.py`
- [ ] `lint-imports --config .importlinter`
- [ ] `python -m compileall -q src tests governance/tools`
- [ ] `python -m build`
- [ ] `twine check dist/*`

## Package Inspection

- [ ] Inspect wheel contents for `catalyst/py.typed`, `LICENSE`, and package modules.
- [ ] Inspect sdist contents to confirm root-level build scaffolding is excluded.
- [ ] Install the wheel in a clean virtual environment.
- [ ] Run `catalyst --version`.
- [ ] Run `catalyst chunk` against a small Markdown fixture.
- [ ] Import `chunk_source`, `emit_projection`, and `PythonAstParser` from a clean environment.

## Publication

- [ ] Upload to TestPyPI first.
- [ ] Install from TestPyPI in a clean environment.
- [ ] Run the CLI smoke test from the installed package.
- [ ] Upload to PyPI.
- [ ] Create a Git tag matching the release version.
