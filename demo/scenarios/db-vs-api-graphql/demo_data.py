from __future__ import annotations

DEMO_EMAIL = "alice@vaagatech.com"
db_status_mapping = {"status": {"SYNCED": "synced"}}
db_plan_mapping = {"planCode": {"PREMIUM": "PRO"}}

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
