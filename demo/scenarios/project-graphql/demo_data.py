from __future__ import annotations

from typing import Any, Callable

account_transforms: dict[str, Callable[[Any], Any]] = {
    "syncedAt": lambda value: (
        "VALID_DATE" if isinstance(value, str) and value and not _is_invalid_date(value) else "INVALID_DATE"
    ),
}


def _is_invalid_date(value: str) -> bool:
    from datetime import datetime

    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return False
    except ValueError:
        return True


account_mapping = {
    "status": {"ACTIVE": "ACTV"},
    "segment": {"ENTERPRISE": "ENT"},
}

orders_mapping: dict[str, dict[str, str]] = {}

sync_mapping = {
    "status": {"ACTIVE": "ACTV"},
}
