# Configuration Reference

`catalyst.toml` records the intended defaults for the package. The current CLI uses built-in defaults; direct policy changes are made through `SelectionPolicy` in library code.

## Package Mode

```toml
[catalyst]
mode = "retrieval"
```

## Source

```toml
[source]
require_lineage = true
lossy_mode = false
```

Catalyst expects source lineage. Lossy normalization must be declared rather than hidden.

## Formation Policy

```toml
[formation]
target_tokens = 650
hard_max_tokens = 1200
prefer_structure = true
allow_semantic_refinement = false
allow_late_chunking = false
require_ast_for_code = true
max_repair_ratio = 0.10
max_orphan_ratio = 0.02
```

Corresponding Python type:

```python
from catalyst.formation.selection.selection_policy import SelectionPolicy
```

Important fields:

- `target_tokens`: preferred soft chunk target.
- `hard_max_tokens`: hard admission limit.
- `prefer_structure`: keep structure-first behavior.
- `allow_semantic_refinement`: permit semantic evidence after structural candidates exist.
- `allow_late_chunking`: specialized mode, disabled by default.
- `require_ast_for_code`: keep code chunking AST-aware.

## Token Budget Semantics

The baseline local path counts whitespace-delimited tokens. This makes default chunking deterministic and dependency-free, but it is not the same as a provider tokenizer.

Implications:

- A long atomic string with no whitespace is one baseline Catalyst token.
- Catalyst does not split inside an atomic source token by default because no source boundary has been observed.
- If an application needs provider-token limits, map provider budgets conservatively before creating `SelectionPolicy`, or add a tokenizer boundary adapter that reports the provider's token view as evidence.
- `hard_max_tokens` is absolute for Catalyst's active token count, not automatically absolute for every downstream model tokenizer.

Catalyst also emits a `source_measure` observation with `character_count`, `byte_count`, `line_count`, `lexical_token_count`, and `max_atomic_run_characters`. Agent and provider adapters can use this evidence to flag source that is small under Catalyst's whitespace baseline but large under a model tokenizer.

## Projection

```toml
[projection]
retrieval = true
audit = true
boundary_inspection = true
```

Every public projection must include `schema_version` and `projection_kind`.

## Governance

```toml
[governance]
keep_rejections = true
fail_on_lost_source = true
fail_on_unversioned_projection = true
fail_on_boundary_adapter_import_inward = true
```

These settings reflect enforced architecture rules and release gates.
