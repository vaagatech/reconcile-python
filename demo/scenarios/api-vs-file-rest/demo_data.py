from __future__ import annotations

from datetime import datetime
from typing import Any


def _valid_date(value: Any, _key=None, _parent=None) -> str:
    if isinstance(value, str):
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return "VALID_DATE"
        except ValueError:
            pass
    return "INVALID_DATE"


date_transform = {"currentdate": _valid_date}
