from __future__ import annotations

from snapline.core import fixtures_dir, test_suite
from snapline.demo_shared.types import ScenarioContext

from .auth import create_auth
from .demo_data import date_transform


class Scenario:
    name = "API vs file (REST + OAuth2 + ignoreFields + transformations)"
    needs_server = True
    needs_database = False

    async def run(self, context: ScenarioContext) -> dict:
        fixtures = fixtures_dir(__file__, {"relativePath": "fixtures"})
        return await test_suite(
            self.name,
            {
                "auth": create_auth(),
                "baseUrl": context.base_url,
                "api": {
                    "endpoint": "/api/v1/user/sync",
                    "method": "POST",
                    "inputFile": str(fixtures / "rest-input.json"),
                    "expectedFile": str(fixtures / "rest-expected.json"),
                    "ignoreFields": ["pincode"],
                    "transformations": date_transform,
                },
            },
        )


scenario = Scenario()
