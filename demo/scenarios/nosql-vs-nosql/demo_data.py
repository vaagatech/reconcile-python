from __future__ import annotations

DEMO_EMAIL = "alice@vaagatech.com"

source_customer = {
    "customerId": "cust_1",
    "email": DEMO_EMAIL,
    "status": "ACTIVE",
    "tier": "gold",
    "profile": {"role": "admin", "department": "engineering"},
}

target_snapshot = {
    "customerId": "cust_1",
    "email": DEMO_EMAIL,
    "status": "ACTIVE",
    "tier": "gold",
    "profile": {"role": "admin", "department": "engineering"},
}
