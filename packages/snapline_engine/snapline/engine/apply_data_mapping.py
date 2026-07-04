from __future__ import annotations

from typing import Any, Callable

from .types import DataMappingMap, FieldMapping
from .utils.deep_clone import deep_clone
from .utils.is_plain_object import is_plain_object


def map_field_value(value: Any, mapping: FieldMapping) -> Any:
    if callable(mapping):
        return mapping(value)

    if is_plain_object(mapping):
        key = str(value)
        if key in mapping:
            return mapping[key]

    return value


def apply_data_mapping(
    data: Any,
    data_mapping: DataMappingMap | None = None,
) -> Any:
    mappings = data_mapping or {}
    if not mappings:
        return data

    def walk(value: Any) -> Any:
        if isinstance(value, list):
            return [walk(item) for item in value]

        if not is_plain_object(value):
            return value

        result: dict[str, Any] = {}
        for key, child in value.items():
            mapping = mappings.get(key)
            if mapping:
                result[key] = map_field_value(child, mapping)
            else:
                result[key] = walk(child)
        return result

    return walk(deep_clone(data))
