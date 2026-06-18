# Contributing

Catalyst contributions should preserve the architecture rather than work around it.

## Setup

```bash
python -m pip install -e ".[dev]"
```

## Before Editing

Read:

- `README.md`
- `docs/README.md`
- `docs/architecture/ARCHITECTURE.md`
- `docs/architecture/SYSTEM_LANGUAGE.md`
- relevant ADRs in `ADRs/`

## Naming Rules

Use native Catalyst terms such as source, observation, evidence, invariant, candidate, chunk graph, projection, boundary, policy, repair, and rejection.

Avoid generic names such as service, manager, controller, repository, processor, worker, utility, and pipeline unless an ADR explicitly admits them.

## Architecture Rules

- Boundary adapters may import provider libraries.
- Internal layers must use Catalyst-native records.
- LLM, embedding, parser, and provider outputs are evidence, not source truth.
- Rejections and repairs must remain inspectable.
- Public projections must be versioned.

## Verification

Run the commands in [Testing](TESTING.md) before opening a PR.

## Pull Request Expectations

- Keep changes scoped.
- Add or update tests for behavior changes.
- Update docs when public behavior changes.
- Update `CHANGELOG.md` for release-visible changes.
