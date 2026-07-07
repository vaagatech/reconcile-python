from __future__ import annotations

import os
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCENARIOS_DIR = REPO_ROOT / "demo" / "scenarios"

AUTH_SCENARIOS = {
    "api-vs-file-rest",
    "api-vs-file-rest-cases",
    "api-vs-file-graphql",
    "api-vs-db-graphql",
    "db-vs-api-graphql",
}

ENV_PY = textwrap.dedent(
    '''\
    from __future__ import annotations

    import os

    from snapline.core import resolve_report_config, write_test_report


    def require_env(name: str) -> str:
        value = os.environ.get(name)
        if not value:
            raise ValueError(f"Set {name} (see .env.example)")
        return value


    def finalize_run(result: dict, suite_name: str) -> dict:
        report_config = resolve_report_config()
        if report_config:
            write_test_report(
                [result],
                report_config,
                {"environment": {"suite": suite_name, "reportFormat": report_config["format"]}},
            )
        return result
    '''
)

AUTH_PY = textwrap.dedent(
    '''\
    from __future__ import annotations

    from snapline.core import auth

    from .env import require_env


    def create_auth():
        base_url = require_env("API_BASE_URL")
        return auth.oauth2(
            {
                "tokenUrl": f"{base_url}/oauth/token",
                "clientId": require_env("CLIENT_ID"),
                "clientSecret": require_env("CLIENT_SECRET"),
            }
        )
    '''
)

DEMO_DATA: dict[str, str] = {
    "api-vs-db-graphql": '''\
from __future__ import annotations

DEMO_EMAIL = "alice@vaagatech.com"

api_status_mapping = {"status": {"synced": "SYNCED"}}
api_plan_mapping = {"planCode": {"PRO": "PREMIUM"}}

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
''',
    "api-vs-db-rest": '''\
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


DEMO_EMAIL = "alice@vaagatech.com"
date_transform = {"currentdate": _valid_date}
api_status_mapping = {"status": {"synced": "SYNCED"}}
''',
    "api-vs-db-soap": '''\
from __future__ import annotations

DEMO_EMAIL = "alice@vaagatech.com"
api_status_mapping = {"status": {"synced": "SYNCED"}}
''',
    "api-vs-file-graphql": '''\
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
''',
    "api-vs-file-rest": '''\
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
''',
    "api-vs-file-rest-cases": '''\
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
no_date_transform = {}
''',
    "db-comparison-transformations": '''\
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


DEMO_EMAIL = "alice@vaagatech.com"
date_transform = {"logged_at": _valid_date}
''',
    "db-vs-api-graphql": '''\
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
''',
    "db-vs-api-rest": '''\
from __future__ import annotations

DEMO_EMAIL = "alice@vaagatech.com"
db_status_mapping = {"status": {"SYNCED": "synced"}}
''',
    "db-vs-api-soap": '''\
from __future__ import annotations

DEMO_EMAIL = "alice@vaagatech.com"
db_status_mapping = {"status": {"SYNCED": "synced"}}
''',
    "db-vs-db-cross-dialect": '''\
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
''',
    "db-vs-db-sqlite": '''\
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
''',
    "nosql-vs-nosql": '''\
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
''',
    "snapline-combined-options": '''\
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


DEMO_EMAIL = "alice@vaagatech.com"
date_transform = {"currentdate": _valid_date}
api_status_mapping = {"status": {"synced": "SYNCED"}}
''',
    "snapline-data-mapping-function": '''\
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
''',
    "snapline-data-mapping-lookup": '''\
from __future__ import annotations

status_lookup = {"status": {"ACTIVE": "ACTV", "ABC": "CBA"}}
wrong_status_lookup = {"status": {"ACTIVE": "WRONG"}}
''',
    "snapline-transformations": '''\
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
date_transform = {"lastLogin": _valid_date, "renewsAt": _valid_date}

enrichment_transforms = {**role_transform, **tier_transform, **date_transform}
role_tier_only_transforms = {**role_transform, **tier_transform}
date_field_transforms = {
    "lastLogin": date_transform["lastLogin"],
    "renewsAt": date_transform["renewsAt"],
}
''',
}


def scaffold() -> None:
    for scenario_dir in sorted(SCENARIOS_DIR.iterdir()):
        if not scenario_dir.is_dir():
            continue
        scenario_id = scenario_dir.name
        (scenario_dir / "env.py").write_text(ENV_PY)
        if scenario_id in AUTH_SCENARIOS:
            (scenario_dir / "auth.py").write_text(AUTH_PY)
        if scenario_id in DEMO_DATA:
            (scenario_dir / "demo_data.py").write_text(DEMO_DATA[scenario_id])
        print(f"scaffolded {scenario_id}")


if __name__ == "__main__":
    scaffold()
