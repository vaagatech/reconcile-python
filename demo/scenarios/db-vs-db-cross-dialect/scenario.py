from __future__ import annotations

from snapline.core import db, seed_db, test_suite
from snapline.demo_shared import DEMO_EMAIL, status_mapping_lookup
from snapline.demo_shared.types import ScenarioContext

SOURCE_DSN = "postgresql://demo/source"
TARGET_DSN = "mysql://demo/target"

USER_SYNC_QUERY = """
  SELECT status, email
  FROM users
  WHERE email = :email
"""


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
                    "query": USER_SYNC_QUERY,
                    "params": {"email": DEMO_EMAIL},
                    "dataMapping": {"status": status_mapping_lookup["status"]},
                }
            },
        )


scenario = Scenario()
