from __future__ import annotations

from pathlib import Path

from reconcile.core import api, test_suite
from reconcile.demo_shared import fixtures_dir
from reconcile.demo_shared.types import ScenarioContext


class Scenario:
    name = "Reconcile: ignoreFields (nested paths)"
    needs_server = True
    needs_database = False

    async def run(self, context: ScenarioContext) -> dict:
        fixtures = fixtures_dir(__file__)
        return await test_suite(
            self.name,
            {
                "baseUrl": context.base_url,
                "api": {
                    **api.rest({"endpoint": "/api/v1/events/tracked", "method": "GET"}),
                    "expectedFile": str(fixtures / "tracked-expected.json"),
                    "ignoreFields": ["metadata.trackedAt", "metadata.requestId"],
                },
            },
        )

scenario = Scenario()
