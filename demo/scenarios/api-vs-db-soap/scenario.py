from __future__ import annotations

from reconcile.core import api, test_suite
from reconcile.demo_shared import api_status_mapping, DEMO_EMAIL, fixtures_dir
from reconcile.demo_shared.types import ScenarioContext


class Scenario:
    name = "API vs DB (SOAP user vs multi-table SQLite JOIN)"
    needs_server = True
    needs_database = True

    async def run(self, context: ScenarioContext) -> dict:
        fixtures = fixtures_dir(__file__)
        return await test_suite(
            self.name,
            {
                "baseUrl": context.base_url,
                "apiToDb": {
                    "api": {
                        **api.soap(
                            {
                                "endpoint": "/soap/user",
                                "soapAction": "GetUser",
                                "inputFile": str(fixtures / "soap-request.xml"),
                            }
                        ),
                        "expectedStatus": 200,
                    },
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
                    "dataMapping": api_status_mapping,
                },
            },
        )


scenario = Scenario()
