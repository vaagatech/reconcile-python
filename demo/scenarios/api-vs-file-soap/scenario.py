from __future__ import annotations

from snapline.core import api, test_suite
from snapline.demo_shared import fixtures_dir
from snapline.demo_shared.types import ScenarioContext


class Scenario:
    name = "API vs file (SOAP)"
    needs_server = True
    needs_database = False

    async def run(self, context: ScenarioContext) -> dict:
        fixtures = fixtures_dir(__file__)
        return await test_suite(
            "8. API vs file (SOAP)",
            {
                "baseUrl": context.base_url,
                "api": {
                    **api.soap(
                        {
                            "endpoint": "/soap/user",
                            "soapAction": "GetUser",
                            "inputFile": str(fixtures / "soap-request.xml"),
                        }
                    ),
                    "expectedFile": str(fixtures / "soap-expected.json"),
                },
            },
        )


scenario = Scenario()
