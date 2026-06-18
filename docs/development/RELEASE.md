# Release

Use this procedure for TestPyPI and PyPI releases.

## Prepare

1. Confirm `pyproject.toml` and `src/catalyst/__init__.py` versions match.
2. Update `CHANGELOG.md`.
3. Run the full verification command set in [Testing](TESTING.md).
4. Review `RELEASE_CHECKLIST.md`.

## Build

```bash
rm -rf dist
python -m build
twine check dist/*
```

## TestPyPI

```bash
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="YOUR_TESTPYPI_TOKEN"
twine upload --repository testpypi dist/*
```

Install from TestPyPI:

```bash
python -m venv /tmp/catalyst-testpypi
/tmp/catalyst-testpypi/bin/python -m pip install \
  --index-url https://test.pypi.org/simple/ \
  --no-deps \
  catalyst-chunker
/tmp/catalyst-testpypi/bin/catalyst --version
```

## PyPI

```bash
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="YOUR_PYPI_TOKEN"
twine upload dist/*
```

After upload, install in a clean environment:

```bash
python -m venv /tmp/catalyst-pypi
/tmp/catalyst-pypi/bin/python -m pip install catalyst-chunker
/tmp/catalyst-pypi/bin/catalyst --version
```

Once a version is uploaded to PyPI, it cannot be replaced. Use a new patch version for fixes.
