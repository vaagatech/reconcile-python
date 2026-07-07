from __future__ import annotations

from snapline.core import fixtures_dir, run_api_fixture_cases
from snapline.demo_shared.types import ScenarioContext

from .auth import create_auth
from .demo_data import account_mapping, account_transforms, orders_mapping, sync_mapping


class Scenario:
    name = "Project GraphQL — 3 operations (Auth0/Okta + fixture cases)"
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
                    "endpoint": "/project/graphql",
                    "protocol": "graphql",
                    "ignoreFields": [],
                },
                "presets": {
                    "transformations": {"account": account_transforms},
                    "dataMapping": {
                        "account": account_mapping,
                        "orders": orders_mapping,
                        "sync": sync_mapping,
                    },
                },
            }
        )


scenario = Scenario()
