from __future__ import annotations

from typing import Any

from .types import TransformationMap
from .utils.deep_clone import deep_clone
from .utils.is_plain_object import is_plain_object


def apply_transformations(
    data: Any,
    transformations: TransformationMap | None = None,
) -> Any:
    transforms = transformations or {}
    if not transforms:
        return data

    def walk(value: Any) -> Any:
        if isinstance(value, list):
            return [walk(item) for item in value]

        if not is_plain_object(value):
            return value

        result: dict[str, Any] = {}
        for key, child in value.items():
            transform = transforms.get(key)
            if transform:
                result[key] = transform(child, key, value)
            else:
                result[key] = walk(child)
        return result

    return walk(deep_clone(data))
