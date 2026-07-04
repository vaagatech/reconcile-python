from __future__ import annotations

from typing import Any

from .diff_values import diff_values


def compare_objects(actual: Any, expected: Any) -> dict[str, Any]:
    diff = diff_values(actual, expected)
    return {"match": diff is None, "diff": diff}
