from __future__ import annotations

from snapline.core import fixtures_dir, run_snapline_fixture_cases
from snapline.demo_shared.types import ScenarioContext

from .demo_data import status_lookup, wrong_status_lookup


class Scenario:
    name = "Snapline: dataMapping lookup table (fixture cases: pass + expected failures)"
    needs_server = False
    needs_database = False

    async def run(self, context: ScenarioContext) -> dict:
        return await run_snapline_fixture_cases(
            {
                "suiteName": self.name,
                "fixturesRoot": str(fixtures_dir(__file__, {"relativePath": "fixtures"})),
                "presets": {
                    "dataMapping": {
                        "warehouseStatus": status_lookup,
                        "wrongStatus": wrong_status_lookup,
                    }
                },
            }
        )


scenario = Scenario()
