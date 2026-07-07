from __future__ import annotations

from snapline.core import db, seed_db, test_suite
from snapline.demo_shared.types import ScenarioContext

from .demo_data import (
    DEMO_EMAIL,
    SOURCE_DSN,
    TARGET_DSN,
    cross_dialect_status_mapping,
    user_sync_query,
)


class Scenario:
    name = "DB vs DB (Postgres source vs MySQL target via seedDb stub)"
    needs_server = False
    needs_database = False

    async def run(self, context: ScenarioContext) -> dict:
        seed_db(SOURCE_DSN, [{"status": "ABC", "email": DEMO_EMAIL}])
        seed_db(TARGET_DSN, [{"status": "CBA", "email": DEMO_EMAIL}])

        return await test_suite(
            self.name,
            {
                "dbComparison": {
                    "sourceDb": db.postgres(SOURCE_DSN),
                    "targetDb": db.mysql(TARGET_DSN),
                    "query": user_sync_query,
                    "params": {"email": DEMO_EMAIL},
                    "dataMapping": cross_dialect_status_mapping,
                }
            },
        )


scenario = Scenario()
