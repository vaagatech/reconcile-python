from __future__ import annotations

from snapline.core import test_suite
from snapline.demo_shared import (
    api_status_mapping,
    DEMO_EMAIL,
    fixtures_dir,
    run_reconcile_fixture_cases,
    status_mapping_function,
    warehouse_plan_mapping,
)
from snapline.demo_shared.types import ScenarioContext


class Scenario:
    name = "Snapline: dataMapping (fixture cases + DB function mapper)"
    needs_server = False
    needs_database = True

    async def run(self, context: ScenarioContext) -> dict:
        fixture_result = await run_reconcile_fixture_cases(
            {
                "suiteName": "Snapline: dataMapping fixture cases (pass + expected failures)",
                "fixturesRoot": str(fixtures_dir(__file__)),
                "presets": {
                    "dataMapping": {
                        "warehouseStatus": status_mapping_function,
                        "warehousePlan": warehouse_plan_mapping,
                        "apiStatusOnly": api_status_mapping,
                    }
                },
            }
        )

        db_result = await test_suite(
            "Snapline: dataMapping (DB function mapper on warehouse)",
            {
                "dbComparison": {
                    "sourceDb": context.database.source_db,
                    "targetDb": context.database.target_db,
                    "query": """
          SELECT c.email, c.status_code AS status
          FROM customers c
          WHERE c.email = :email
        """,
                    "params": {"email": DEMO_EMAIL},
                    "dataMapping": status_mapping_function,
                }
            },
        )

        return {
            "name": self.name,
            "passed": fixture_result["passed"] and db_result["passed"],
            "results": [*fixture_result["results"], *db_result["results"]],
        }


scenario = Scenario()
