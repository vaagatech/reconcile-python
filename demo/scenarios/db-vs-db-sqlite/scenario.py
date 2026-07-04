from __future__ import annotations

from reconcile.core import test_suite
from reconcile.demo_shared import (
    DEMO_EMAIL,
    status_mapping_lookup,
    warehouse_customer_join_query,
    warehouse_order_join_query,
    warehouse_order_status_mapping,
)
from reconcile.demo_shared.types import ScenarioContext


class Scenario:
    name = "DB vs DB (SQLite multi-table warehouse + dataMapping)"
    needs_server = False
    needs_database = True

    async def run(self, context: ScenarioContext) -> dict:
        source_db = context.database.source_db
        target_db = context.database.target_db

        customer_result = await test_suite(
            "DB vs DB: customer domain (profiles + subscriptions)",
            {
                "dbComparison": {
                    "sourceDb": source_db,
                    "targetDb": target_db,
                    "query": warehouse_customer_join_query,
                    "params": {"email": DEMO_EMAIL},
                    "dataMapping": status_mapping_lookup,
                }
            },
        )

        orders_result = await test_suite(
            "DB vs DB: orders (fulfillment status codes)",
            {
                "dbComparison": {
                    "sourceDb": source_db,
                    "targetDb": target_db,
                    "query": warehouse_order_join_query,
                    "params": {"email": DEMO_EMAIL},
                    "dataMapping": warehouse_order_status_mapping,
                }
            },
        )

        return {
            "name": self.name,
            "passed": customer_result["passed"] and orders_result["passed"],
            "results": [*customer_result["results"], *orders_result["results"]],
        }


scenario = Scenario()
