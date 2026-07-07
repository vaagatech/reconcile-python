from __future__ import annotations

from typing import Any


def _status_mapping_function(value: Any) -> Any:
    if value == "ABC":
        return "CBA"
    if value == "ACTIVE":
        return "ACTV"
    return value


DEMO_EMAIL = "alice@vaagatech.com"
status_mapping_function = {
    "status": lambda value, _key=None, _parent=None: _status_mapping_function(value),
    "status_code": lambda value, _key=None, _parent=None: "ACTV" if value == "ACTIVE" else value,
}
warehouse_plan_mapping = {"plan_code": {"PRO": "PREMIUM"}, "planCode": {"PRO": "PREMIUM"}}
api_status_mapping = {"status": {"synced": "SYNCED"}}
