from __future__ import annotations

from snapline.core import fixtures_dir, run_api_fixture_cases
from snapline.demo_shared.types import ScenarioContext

from .auth import create_auth
from .demo_data import (
    date_field_transforms,
    graphql_account_transforms,
    graphql_plan_mapping,
    graphql_snapshot_transforms,
    graphql_status_mapping,
    role_tier_only_transforms,
)


class Scenario:
    name = "API vs file (GraphQL + OAuth2 fixture cases: pass + expected failures)"
    needs_server = True
    needs_database = False

    async def run(self, context: ScenarioContext) -> dict:
        return await run_api_fixture_cases(
            {
                "suiteName": self.name,
                "fixturesRoot": str(fixtures_dir(__file__, {"relativePath": "fixtures"})),
                "baseUrl": context.base_url,
                "auth": create_auth(),
                "defaults": {
                    "endpoint": "/graphql",
                    "protocol": "graphql",
                    "dataPath": "customerAccount",
                    "ignoreFields": ["metadata.traceId", "metadata.syncedAt"],
                    "transformations": "graphqlAccount",
                    "dataMapping": "graphqlAccount",
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
