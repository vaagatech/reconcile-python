from __future__ import annotations

import json
from typing import Any


def stable_stringify(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))
