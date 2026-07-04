from __future__ import annotations

from snapline.core import api, test_suite
from snapline.demo_shared import (
    api_plan_mapping,
    api_status_mapping,
    app_customer_join_query,
    create_demo_auth,
    DEMO_EMAIL,
    fixtures_dir,
)
from snapline.demo_shared.types import ScenarioContext


class Scenario:
    name = "API vs DB (GraphQL + OAuth2 snapshot vs multi-table SQLite JOIN)"
    needs_server = True
    needs_database = True

    async def run(self, context: ScenarioContext) -> dict:
        fixtures = fixtures_dir(__file__)
        return await test_suite(
            self.name,
            {
                "auth": create_demo_auth(context.base_url),
                "baseUrl": context.base_url,
                "apiToDb": {
                    "api": {
                        **api.graphql(
                            {
                                "endpoint": "/graphql",
                                "query": """
              query CustomerSnapshot($email: String!) {
                customerSnapshot(email: $email) {
                  email
                  status
                  tier
                  role
                  department
                  planCode
                  renewsAt
                  lastLogin
                }
              }
            """,
                                "variablesFile": str(fixtures / "graphql-variables.json"),
                                "dataPath": "customerSnapshot",
                            }
                        ),
                        "expectedStatus": 200,
                    },
                    "db": {
                        "db": context.database.app_db,
                        "query": app_customer_join_query,
                        "params": {"email": DEMO_EMAIL},
                    },
                    "dataMapping": {
                        **api_status_mapping,
                        **api_plan_mapping,
                    },
                },
            },
        )


scenario = Scenario()
