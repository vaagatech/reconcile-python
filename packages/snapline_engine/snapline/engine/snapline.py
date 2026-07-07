from __future__ import annotations

from typing import Any

from .apply_data_mapping import apply_data_mapping
from .apply_transformations import apply_transformations
from .compare_objects import compare_objects
from .strip_fields import strip_fields
from .types import SnaplineOptions
from .utils.deep_clone import deep_clone


def snapline(
    live_data: Any,
    expected_data: Any,
    options: SnaplineOptions | dict[str, Any] | None = None,
) -> dict[str, Any]:
    opts = options or {}
    ignore_fields = opts.get("ignoreFields", [])
    transformations = opts.get("transformations", {})
    data_mapping = opts.get("dataMapping", {})

    processed = deep_clone(live_data)
    processed = strip_fields(processed, ignore_fields)
    processed = apply_transformations(processed, transformations)
    processed = apply_data_mapping(processed, data_mapping)

    expected = deep_clone(expected_data)
    expected = strip_fields(expected, ignore_fields)

    comparison = compare_objects(processed, expected)
    return {
        "match": comparison["match"],
        "processed": processed,
        "expected": expected,
        "diff": comparison["diff"],
    }
