from __future__ import annotations

DEMO_EMAIL = "alice@vaagatech.com"

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
warehouse_order_status_mapping = {"status": {"SHIPPED": "DELIVERED"}}

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
