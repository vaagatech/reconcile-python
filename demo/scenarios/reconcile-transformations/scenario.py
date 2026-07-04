from __future__ import annotations

from snapline.demo_shared import (
    date_field_transforms,
    enrichment_transforms,
    fixtures_dir,
    role_tier_only_transforms,
    run_reconcile_fixture_cases,
)
from snapline.demo_shared.types import ScenarioContext


class Scenario:
    name = "Snapline: transformations (fixture cases: pass + expected failures)"
    needs_server = False
    needs_database = False

    async def run(self, context: ScenarioContext) -> dict:
        return await run_reconcile_fixture_cases(
            {
                "suiteName": self.name,
                "fixturesRoot": str(fixtures_dir(__file__)),
                "presets": {
                    "transformations": {
                        "enrichment": enrichment_transforms,
                        "roleTierOnly": role_tier_only_transforms,
                        "datesOnly": date_field_transforms,
                    }
                },
            }
        )


scenario = Scenario()
