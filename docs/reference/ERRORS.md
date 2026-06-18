# Error Records

Catalyst errors expose structured records through `to_dict()`.

## Common Errors

```python
from catalyst.shared.errors import EmptySourceError, InvariantViolation
from catalyst.formation.selection import SelectionFailure
```

| Error | Code | Meaning |
|---|---|---|
| `EmptySourceError` | `source.empty` | Source material contains no chunkable text. |
| `SelectionFailure` | `selection.failure` | No candidate set satisfied selection policy. |
| `InvariantViolation` | `invariant.violation` | A hard invariant blocked admission. |

## Shape

```python
try:
    ...
except CatalystError as error:
    record = error.to_dict()
```

The record shape is:

```json
{
  "code": "source.empty",
  "message": "source contains no chunkable text",
  "details": {}
}
```

`SelectionFailure` includes rejection records in `details["rejections"]`.
