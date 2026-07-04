from __future__ import annotations

from typing import Any


def is_plain_object(value: Any) -> bool:
    return isinstance(value, dict)
