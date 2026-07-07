from __future__ import annotations

from snapline.core import fixtures_dir, run_api_fixture_cases
from snapline.demo_shared.types import ScenarioContext

from .auth import create_auth
from .demo_data import date_transform, no_date_transform


class Scenario:
    name = "API vs file (REST fixture cases + OAuth2: pass + expected failures)"
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
                    "endpoint": "/api/v1/user/sync",
                    "protocol": "rest",
                    "ignoreFields": ["pincode"],
                    "transformations": "datesOnly",
                },
                "presets": {
                    "transformations": {
                        "datesOnly": date_transform,
                        "noDates": no_date_transform,
                    }
                },
            }
        )


scenario = Scenario()
