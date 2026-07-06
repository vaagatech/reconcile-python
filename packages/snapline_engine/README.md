# snapline-engine

Deep JSON reconciliation engine for declarative snapshot testing. Compare live API or database payloads against JSON fixtures while ignoring volatile fields, normalizing dynamic values, and mapping cross-system schema differences.

## Install

```bash
pip install snapline-engine
```

## Quick start

```python
from snapline.engine import reconcile

result = reconcile(
    {"id": "1", "status": "ok", "traceId": "abc"},
    {"id": "1", "status": "ok"},
    {"ignoreFields": ["traceId"]},
)
print(result["match"])
```

## Documentation

Full docs, demos, and the rest of the Snapline Python packages:

https://github.com/vaagatech/snapline-python
