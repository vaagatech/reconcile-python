from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timezone

DEMO_EMAIL = "alice@vaagatech.com"
DEMO_ORDER_ID = "ord_1001"


@dataclass(frozen=True)
class DemoDomain:
    email: str = DEMO_EMAIL
    api_status: str = "synced"
    app_db_status: str = "SYNCED"
    warehouse_source_status: str = "ACTIVE"
    warehouse_target_status: str = "ACTV"
    tier: str = "gold"
    role: str = "member"
    department: str = "engineering"
    api_plan_code: str = "PRO"
    warehouse_source_plan: str = "PRO"
    warehouse_target_plan: str = "PREMIUM"
    renews_at: str = "2026-07-04T10:00:00.000Z"
    last_login: str = "2026-07-04T09:30:00.000Z"
    audit_logged_at: str = "2026-07-04T10:00:00.000Z"
    order_status: str = "shipped"
    warehouse_source_order_status: str = "SHIPPED"
    warehouse_target_order_status: str = "DELIVERED"
    order_total: float = 149.99
    order_shipped_at: str = "2026-07-04T08:15:00.000Z"


demo_domain = DemoDomain()


def volatile_trace_id() -> str:
    return f"trace_{random.randint(0, 999_999)}"


def volatile_synced_at() -> str:
    return datetime.now(timezone.utc).isoformat()


def volatile_pincode() -> str:
    return f"{random.randint(100000, 999999)}"
