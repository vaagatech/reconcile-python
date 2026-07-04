from __future__ import annotations

from snapline.core import api, test_suite
from snapline.demo_shared import api_status_mapping, date_transform, DEMO_EMAIL
from snapline.demo_shared.types import ScenarioContext


class Scenario:
    name = "API vs DB (REST profile vs multi-table SQLite JOIN)"
    needs_server = True
    needs_database = True

    async def run(self, context: ScenarioContext) -> dict:
        return await test_suite(
            self.name,
            {
                "baseUrl": context.base_url,
                "apiToDb": {
                    "api": api.rest(
                        {
                            "endpoint": f"/api/v1/users/profile?email={DEMO_EMAIL}",
                            "method": "GET",
                        }
                    ),
                    "db": {
                        "db": context.database.app_db,
                        "query": """
            SELECT c.email, c.status, p.role
            FROM customers c
            INNER JOIN customer_profiles p ON c.email = p.email
            WHERE c.email = :email
          """,
                        "params": {"email": DEMO_EMAIL},
                    },
                    "ignoreFields": ["traceId", "currentdate"],
                    "transformations": date_transform,
                    "dataMapping": api_status_mapping,
                },
            },
        )


scenario = Scenario()
