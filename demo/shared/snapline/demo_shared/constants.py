from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

from .demo_domain import DEMO_EMAIL

Transformation = Callable[[Any], Any]


def _valid_date(value: Any, _key=None, _parent=None) -> str:
    if isinstance(value, str):
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return "VALID_DATE"
        except ValueError:
            pass
    return "INVALID_DATE"


date_transform: dict[str, Transformation] = {
    "currentdate": _valid_date,
    "logged_at": _valid_date,
    "lastLogin": _valid_date,
    "renewsAt": _valid_date,
    "shippedAt": _valid_date,
}

role_transform = {"role": lambda value, _key=None, _parent=None: str(value).upper()}
tier_transform = {"tier": lambda value, _key=None, _parent=None: str(value).upper()}
order_status_transform = {"status": lambda value, _key=None, _parent=None: str(value).upper()}

enrichment_transforms = {**role_transform, **tier_transform, **date_transform}


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

status_mapping_lookup = {
    "status": {
        "ABC": "CBA",
        "ACTIVE": "ACTV",
        "synced": "SYNCED",
        "SYNCED": "synced",
        "shipped": "DELIVERED",
        "SHIPPED": "DELIVERED",
    },
    "status_code": {"ACTIVE": "ACTV"},
    "plan_code": {"PRO": "PREMIUM"},
    "planCode": {"PRO": "PREMIUM"},
}


def _status_mapping_function(value: Any) -> Any:
    if value == "ABC":
        return "CBA"
    if value == "ACTIVE":
        return "ACTV"
    return value


status_mapping_function = {
    "status": lambda value, _key=None, _parent=None: _status_mapping_function(value),
    "status_code": lambda value, _key=None, _parent=None: "ACTV" if value == "ACTIVE" else value,
}

api_status_mapping = {"status": {"synced": "SYNCED"}}
db_status_mapping = {"status": {"SYNCED": "synced"}}
db_plan_mapping = {"planCode": {"PREMIUM": "PRO"}}
api_plan_mapping = {"planCode": {"PRO": "PREMIUM"}}
graphql_status_mapping = {"status": {"synced": "ACTIVE"}}
graphql_plan_mapping = {"planCode": {"PRO": "premium"}}
graphql_subscription_mapping = {"planCode": {"PRO": "premium"}}
warehouse_plan_mapping = {"plan_code": {"PRO": "PREMIUM"}, "planCode": {"PRO": "PREMIUM"}}
warehouse_order_status_mapping = {"status": {"SHIPPED": "DELIVERED"}}

app_customer_join_query = """
  SELECT
    c.email,
    c.status,
    c.tier,
    c.last_login AS lastLogin,
    p.role,
    p.department,
    s.plan_code AS planCode,
    s.renews_at AS renewsAt
  FROM customers c
  INNER JOIN customer_profiles p ON c.email = p.email
  INNER JOIN customer_subscriptions s ON c.email = s.email
  WHERE c.email = :email
"""

warehouse_customer_join_query = """
  SELECT
    c.email,
    c.status_code AS status,
    p.role,
    p.department,
    s.plan_code AS planCode,
    s.renews_at AS renewsAt
  FROM customers c
  INNER JOIN customer_profiles p ON c.email = p.email
  INNER JOIN customer_subscriptions s ON c.email = s.email
  WHERE c.email = :email
"""

warehouse_order_join_query = """
  SELECT
    o.order_id AS orderId,
    o.email,
    o.status,
    o.amount AS total,
    o.shipped_at AS shippedAt
  FROM orders o
  WHERE o.email = :email
"""

warehouse_order_by_id_query = """
  SELECT
    order_id AS orderId,
    email,
    status,
    amount AS total,
    shipped_at AS shippedAt
  FROM orders
  WHERE order_id = :orderId
"""
