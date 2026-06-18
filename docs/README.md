# Catalyst Documentation

This directory holds the user and developer documentation for Catalyst Chunker.

## Start Here

- [Quickstart](guides/QUICKSTART.md): install, chunk one file, inspect outputs.
- [CLI Guide](guides/CLI.md): command reference and output behavior.
- [Library Usage](guides/LIBRARY_USAGE.md): use Catalyst inside Python software.
- [Agentic Integration](guides/AGENTIC_INTEGRATION.md): use Catalyst with agents and local LLMs without making model output source truth.
- [Retrieval Ingestion](guides/RETRIEVAL_INGESTION.md): map retrieval projections into app-owned ingestion records.
- [Telemetry](guides/TELEMETRY.md): optional telemetry event names and adapters.

## Reference

- [API Reference](reference/API.md): public import paths for the pre-1.0 package.
- [Projection Schemas](reference/PROJECTIONS.md): public record kinds and schema compatibility.
- [Configuration](reference/CONFIGURATION.md): current `catalyst.toml` and policy fields.
- [Stable IDs](reference/STABLE_IDS.md): deterministic ID algorithm and compatibility notes.
- [Error Records](reference/ERRORS.md): structured caller-facing errors.

## Architecture

- [Architecture](architecture/ARCHITECTURE.md): applied layer map and default flow.
- [Boundaries](architecture/BOUNDARIES.md): ports, adapters, and provider translation rules.
- [Invariants](architecture/INVARIANTS.md): invariant names, behavior, and tests.
- [System Language](architecture/SYSTEM_LANGUAGE.md): accepted and rejected project vocabulary.
- [Decision Ledger](architecture/DECISION_LEDGER.md): ADR status index.

## Development

- [Roadmap](development/ROADMAP.md): sequenced post-0.1.3 work and current priorities.
- [Contributing](development/CONTRIBUTING.md): local setup and contribution rules.
- [Testing](development/TESTING.md): verification commands and test taxonomy.
- [Release](development/RELEASE.md): TestPyPI/PyPI release procedure.
- [Security](development/SECURITY.md): safe use in file-processing and agentic contexts.
- [Examples](examples/README.md): small CLI and library examples.
