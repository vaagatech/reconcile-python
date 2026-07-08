# snapline-engine

Deep JSON reconciliation engine for declarative snapshot testing. Compare live API or database payloads against JSON fixtures while ignoring volatile fields, normalizing dynamic values, and mapping cross-system schema differences.

## Install

```bash
pip install snapline-engine
```

## Quick start

```python
from snapline.engine import snapline

result = snapline(
    {"id": "1", "status": "ok", "traceId": "abc"},
    {"id": "1", "status": "ok"},
    {"ignoreFields": ["traceId"]},
)
print(result["match"])
```

## Documentation

**https://vaagatech.github.io/snapline-python/** · [Node.js docs](https://vaagatech.github.io/snapline/) · [Snapline Hub](https://github.com/vaagatech/snapline-hub)

Repository: https://github.com/vaagatech/snapline-python
