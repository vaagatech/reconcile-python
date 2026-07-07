from __future__ import annotations

from snapline.core import test_suite
from snapline.demo_shared.types import ScenarioContext

from .demo_data import DEMO_EMAIL, date_transform


class Scenario:
    name = "Snapline: transformations (DB vs DB + SQLite)"
    needs_server = False
    needs_database = True

    async def run(self, context: ScenarioContext) -> dict:
        return await test_suite(
            self.name,
            {
                "dbComparison": {
                    "sourceDb": context.database.audit_source_db,
                    "targetDb": context.database.audit_target_db,
                    "query": """
          SELECT email, logged_at, status
          FROM users_audit
          WHERE email = :email
        """,
                    "params": {"email": DEMO_EMAIL},
                    "transformations": date_transform,
                }
            },
        )


scenario = Scenario()
