# CLI Guide

The `catalyst` command is a boundary presentation layer over Catalyst operations.

## Version

```bash
catalyst --version
```

## Chunk

```bash
catalyst chunk SOURCE --out chunks.jsonl --audit audit.json
```

Inputs:

- `SOURCE`: local file path.
- `--out`: optional retrieval JSONL output path.
- `--audit`: optional audit JSON output path.

If `--out` is omitted, retrieval records are printed to stdout.

## Inspect Boundaries

```bash
catalyst inspect-boundaries SOURCE --out boundaries.json
```

Emits a `boundary_inspection` projection with observed boundary candidates and scores.

## Compare Strategies

```bash
catalyst compare-strategies SOURCE --out candidate-evaluation.json
```

Compares candidate sets, hard gate results, soft metrics, rejections, repairs, and the selected graph preview.

## Explain Chunk

```bash
catalyst explain-chunk chunks.jsonl CHUNK_ID
```

Reads a retrieval JSONL file and prints the matching chunk record.

## Audit

```bash
catalyst audit audit.json
```

Prints a compact audit summary containing schema version, projection kind, source ID, lost spans, violation count, rejection count, and warning count.

## Retrieval Sanity

```bash
catalyst retrieval-sanity fixtures.json --out retrieval-sanity.json
```

Runs diagnostic fixtures across admitted strategies. The report includes held-out lexical `recall_at_1`, `recall_at_3`, `mrr`, ranked candidate IDs, strategy cost, and hard invariant status. These scores never override hard invariants.

## Output Contract

Every machine-readable public output includes:

- `schema_version`
- `projection_kind`

If a command writes JSONL, each line is one complete JSON record.
