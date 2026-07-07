from __future__ import annotations

from snapline.core import nosql, test_suite
from snapline.demo_shared.types import ScenarioContext

from .demo_data import DEMO_EMAIL, source_customer, target_snapshot


class Scenario:
    name = "NoSQL vs NoSQL (document stores + linkKeys)"
    needs_server = False
    needs_database = False

    async def run(self, context: ScenarioContext) -> dict:
        source_store = nosql.memory()
        target_store = nosql.memory()

        nosql.seed(source_store, "customers", [source_customer])
        nosql.seed(target_store, "customer_snapshots", [target_snapshot])

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
