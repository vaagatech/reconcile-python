from __future__ import annotations

import copy
from typing import Any


def deep_clone(value: Any) -> Any:
    return copy.deepcopy(value)
