from __future__ import annotations

from snapline.core import nosql, test_suite
from snapline.demo_shared import DEMO_EMAIL
from snapline.demo_shared.types import ScenarioContext

SOURCE_CUSTOMER = {
    "customerId": "cust_1",
    "email": DEMO_EMAIL,
    "status": "ACTIVE",
    "tier": "gold",
    "profile": {"role": "admin", "department": "engineering"},
}

TARGET_SNAPSHOT = {
    "customerId": "cust_1",
    "email": DEMO_EMAIL,
    "status": "ACTIVE",
    "tier": "gold",
    "profile": {"role": "admin", "department": "engineering"},
}


class Scenario:
    name = "NoSQL vs NoSQL (document stores + linkKeys)"
    needs_server = False
    needs_database = False

    async def run(self, context: ScenarioContext) -> dict:
        source_store = nosql.memory()
        target_store = nosql.memory()

        nosql.seed(source_store, "customers", [SOURCE_CUSTOMER])
        nosql.seed(target_store, "customer_snapshots", [TARGET_SNAPSHOT])

        return await test_suite(
            self.name,
            {
                "dbComparison": {
                    "sourceDb": source_store,
                    "targetDb": target_store,
                    "sourceCollection": "customers",
                    "targetCollection": "customer_snapshots",
                    "sourceFilter": {"email": DEMO_EMAIL},
                    "linkKeys": {"customerId": "customerId"},
                }
            },
        )


scenario = Scenario()
