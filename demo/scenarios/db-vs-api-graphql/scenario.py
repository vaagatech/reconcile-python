from __future__ import annotations

from snapline.core import api, test_suite
from snapline.demo_shared.types import ScenarioContext

from .auth import create_auth
from .demo_data import DEMO_EMAIL, app_customer_join_query, db_plan_mapping, db_status_mapping


class Scenario:
    name = "DB vs API (OAuth2 GraphQL snapshot vs multi-table SQLite JOIN)"
    needs_server = True
    needs_database = True

    async def run(self, context: ScenarioContext) -> dict:
        return await test_suite(
            self.name,
            {
                "auth": create_auth(),
                "baseUrl": context.base_url,
                "dbToApi": {
                    "db": {
                        "db": context.database.app_db,
                        "query": app_customer_join_query,
                        "params": {"email": DEMO_EMAIL},
                    },
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
                                "dataPath": "customerSnapshot",
                            }
                        ),
                        "expectedStatus": 200,
                    },
                    "inputFromDb": True,
                    "dataMapping": {
                        **db_status_mapping,
                        **db_plan_mapping,
                    },
                },
            },
        )


scenario = Scenario()
