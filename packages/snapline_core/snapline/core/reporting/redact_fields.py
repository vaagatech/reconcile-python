from __future__ import annotations

from copy import deepcopy
from typing import Any

REDACTED = "[REDACTED]"


def _set_nested(target: dict[str, Any], field_path: str, value: Any) -> None:
    parts = field_path.split(".")
    cursor: dict[str, Any] = target

    for part in parts[:-1]:
        next_value = cursor.get(part)
        if not isinstance(next_value, dict):
            return
        cursor = next_value

    if parts[-1]:
        cursor[parts[-1]] = value


def redact_fields(data: Any, fields: list[str] | None = None) -> Any:
    if not fields or data is None:
        return data

    cloned = deepcopy(data)

    if isinstance(cloned, list):
        return [redact_fields(item, fields) for item in cloned]

    if not isinstance(cloned, dict):
        return cloned

    top_level = {field for field in fields if "." not in field}
    nested = [field for field in fields if "." in field]

    for key in top_level:
        if key in cloned:
            cloned[key] = REDACTED

    for path in nested:
        _set_nested(cloned, path, REDACTED)

    return cloned


def redact_suite_results(suites: list[dict[str, Any]], fields: list[str] | None = None) -> list[dict[str, Any]]:
    if not fields:
        return suites

    return [
        {
            **suite,
            "results": [redact_fields(step, fields) for step in suite.get("results", [])],
        }
        for suite in suites
    ]
