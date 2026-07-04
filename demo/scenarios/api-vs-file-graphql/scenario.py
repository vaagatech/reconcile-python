from __future__ import annotations

from reconcile.demo_shared import (
    create_demo_auth,
    date_field_transforms,
    fixtures_dir,
    graphql_account_transforms,
    graphql_plan_mapping,
    graphql_snapshot_transforms,
    graphql_status_mapping,
    role_tier_only_transforms,
    run_api_fixture_cases,
)
from reconcile.demo_shared.types import ScenarioContext


class Scenario:
    name = "API vs file (GraphQL + OAuth2 fixture cases: pass + expected failures)"
    needs_server = True
    needs_database = False

    async def run(self, context: ScenarioContext) -> dict:
        return await run_api_fixture_cases(
            {
                "suiteName": self.name,
                "fixturesRoot": str(fixtures_dir(__file__)),
                "baseUrl": context.base_url,
                "auth": create_demo_auth(context.base_url),
                "defaults": {
                    "endpoint": "/graphql",
                    "protocol": "graphql",
                },
                "presets": {
                    "transformations": {
                        "graphqlAccount": graphql_account_transforms,
                        "graphqlSnapshot": graphql_snapshot_transforms,
                        "roleTierOnly": role_tier_only_transforms,
                        "datesOnly": date_field_transforms,
                    },
                    "dataMapping": {
                        "graphqlAccount": {
                            **graphql_status_mapping,
                            **graphql_plan_mapping,
                        },
                        "planOnly": graphql_plan_mapping,
                        "statusOnly": graphql_status_mapping,
                    },
                },
            }
        )


scenario = Scenario()
