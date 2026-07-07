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


role_transform = {"role": lambda value, _key=None, _parent=None: str(value).upper()}
tier_transform = {"tier": lambda value, _key=None, _parent=None: str(value).upper()}
date_transform = {
    "lastLogin": _valid_date,
    "renewsAt": _valid_date,
    "shippedAt": _valid_date,
}


def _transform_orders(value: Any, _key=None, _parent=None) -> Any:
    if not isinstance(value, list):
        return value
    result = []
    for order in value:
        if not isinstance(order, dict):
            result.append(order)
            continue
        row = dict(order)
        row["status"] = str(row.get("status", "")).upper()
        row["shippedAt"] = _valid_date(row.get("shippedAt"))
        result.append(row)
    return result


graphql_account_transforms = {
    **role_transform,
    **tier_transform,
    "lastLogin": date_transform["lastLogin"],
    "renewsAt": date_transform["renewsAt"],
    "orders": _transform_orders,
}
graphql_snapshot_transforms = {
    **role_transform,
    **tier_transform,
    "lastLogin": date_transform["lastLogin"],
    "renewsAt": date_transform["renewsAt"],
}
role_tier_only_transforms = {**role_transform, **tier_transform}
date_field_transforms = {
    "lastLogin": date_transform["lastLogin"],
    "renewsAt": date_transform["renewsAt"],
    "orders": _transform_orders,
}
graphql_status_mapping = {"status": {"synced": "ACTIVE"}}
graphql_plan_mapping = {"planCode": {"PRO": "premium"}}
