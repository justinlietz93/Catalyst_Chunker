# Security

Catalyst processes local source files and may be embedded in agentic applications. Treat source input and external tool output as untrusted.

## File Inputs

- Validate file paths before passing them to the CLI or source loader.
- Avoid giving agents unrestricted write access to output locations.
- Keep audit records for source IDs, spans, warnings, repairs, and violations.

## External Tools

Docling, ast-grep, embedding models, tokenizers, and LLM providers must remain boundary mechanisms.

Provider output must be translated into Catalyst-native records before internal use.

## LLM Output

LLM output is not source truth.

If model suggestions are retained, record prompt ID, policy ID, model identity, confidence, and rejected alternatives. Keep those records audit-visible.

## Reporting Issues

For a public release, use the GitHub issue tracker for non-sensitive issues. For sensitive issues, coordinate privately with the package maintainer until a disclosure process is established.
