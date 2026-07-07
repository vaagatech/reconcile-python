from __future__ import annotations

DEMO_EMAIL = "alice@vaagatech.com"
SOURCE_DSN = "postgresql://demo/source"
TARGET_DSN = "mysql://demo/target"
cross_dialect_status_mapping = {"status": {"ABC": "CBA"}}

user_sync_query = """
  SELECT status, email
  FROM users
  WHERE email = :email
"""
