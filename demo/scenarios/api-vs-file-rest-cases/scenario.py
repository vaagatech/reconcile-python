from __future__ import annotations

from snapline.demo_shared import (
    create_demo_auth,
    date_transform,
    fixtures_dir,
    run_api_fixture_cases,
)
from snapline.demo_shared.types import ScenarioContext

no_date_transform: dict = {}


class Scenario:
    name = "API vs file (REST fixture cases + OAuth2: pass + expected failures)"
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
