from __future__ import annotations

from typing import Any

from .utils.is_plain_object import is_plain_object
from .utils.stable_stringify import stable_stringify


def diff_values(
    actual: Any,
    expected: Any,
    path_prefix: str = "",
) -> dict[str, Any] | None:
    if actual == expected:
        return None

    actual_type = "array" if isinstance(actual, list) else type(actual).__name__
    expected_type = "array" if isinstance(expected, list) else type(expected).__name__

    if actual_type != expected_type:
        return {
            "path": path_prefix or "(root)",
            "actual": actual,
            "expected": expected,
            "message": f"Type mismatch: {actual_type} !== {expected_type}",
        }

    if not is_plain_object(actual) and not isinstance(actual, list):
        return {
            "path": path_prefix or "(root)",
            "actual": actual,
            "expected": expected,
            "message": "Value mismatch",
        }

    if isinstance(actual, list) and isinstance(expected, list):
        if len(actual) != len(expected):
            return {
                "path": path_prefix or "(root)",
                "actual": len(actual),
                "expected": len(expected),
                "message": "Array length mismatch",
            }

        for index, (actual_item, expected_item) in enumerate(zip(actual, expected)):
            child_path = f"{path_prefix}[{index}]" if path_prefix else f"[{index}]"
            child_diff = diff_values(actual_item, expected_item, child_path)
            if child_diff:
                return child_diff
        return None

    if not is_plain_object(actual) or not is_plain_object(expected):
        return {
            "path": path_prefix or "(root)",
            "actual": actual,
            "expected": expected,
            "message": "Value mismatch",
        }

    actual_keys = sorted(actual.keys())
    expected_keys = sorted(expected.keys())

    if stable_stringify(actual_keys) != stable_stringify(expected_keys):
        return {
            "path": path_prefix or "(root)",
            "actual": actual_keys,
            "expected": expected_keys,
            "message": "Object key mismatch",
        }

    for key in actual_keys:
        child_path = f"{path_prefix}.{key}" if path_prefix else key
        child_diff = diff_values(actual[key], expected[key], child_path)
        if child_diff:
            return child_diff

    return None
