from __future__ import annotations

from snapline.demo_shared import fixtures_dir, run_reconcile_fixture_cases, status_mapping_lookup
from snapline.demo_shared.types import ScenarioContext

wrong_status_lookup = {"status": {"ACTIVE": "WRONG"}}


class Scenario:
    name = "Snapline: dataMapping lookup table (fixture cases: pass + expected failures)"
    needs_server = False
    needs_database = False

    async def run(self, context: ScenarioContext) -> dict:
        return await run_reconcile_fixture_cases(
            {
                "suiteName": self.name,
                "fixturesRoot": str(fixtures_dir(__file__)),
                "presets": {
                    "dataMapping": {
                        "warehouseStatus": status_mapping_lookup,
                        "wrongStatus": wrong_status_lookup,
                    }
                },
            }
        )


scenario = Scenario()
