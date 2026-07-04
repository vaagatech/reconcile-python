from __future__ import annotations

from typing import Any

from .utils.deep_clone import deep_clone
from .utils.is_plain_object import is_plain_object


def _remove_nested(target: Any, field_path: str) -> None:
    parts = field_path.split(".")
    cursor: Any = target if is_plain_object(target) else None

    for part in parts[:-1]:
        if not part or not is_plain_object(cursor) or part not in cursor:
            return
        cursor = cursor[part]

    last_key = parts[-1]
    if not last_key or cursor is None:
        return

    if is_plain_object(cursor):
        cursor.pop(last_key, None)


def strip_fields(data: Any, ignore_fields: list[str] | None = None) -> Any:
    fields = ignore_fields or []
    if not fields:
        return data

    top_level_keys = {field for field in fields if "." not in field}
    nested_paths = [field for field in fields if "." in field]

    def walk(value: Any) -> Any:
        if isinstance(value, list):
            return [walk(item) for item in value]

        if not is_plain_object(value):
            return value

        result: dict[str, Any] = {}
        for key, child in value.items():
            if key in top_level_keys:
                continue
            result[key] = walk(child)

        for field_path in nested_paths:
            _remove_nested(result, field_path)

        return result

    return walk(deep_clone(data))
