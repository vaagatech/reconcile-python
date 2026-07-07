"""Database vs database reconciliation example."""
import asyncio
import sys

from snapline.core import db, seed_db, test_suite


async def main() -> int:
    seed_db(
        "postgresql://localhost:5432/src_db",
        [{"status": "ABC", "email": "alice@example.com"}],
    )
    seed_db(
        "mysql://root@localhost:3306/target_db",
        [{"status": "CBA", "email": "alice@example.com"}],
    )

    result = await test_suite(
        "DB Sync Check",
        {
            "dbComparison": {
                "sourceDb": db.postgres("postgresql://localhost:5432/src_db"),
                "targetDb": db.mysql("mysql://root@localhost:3306/target_db"),
                "query": "SELECT status, email FROM users WHERE email = :email",
                "params": {"email": "alice@example.com"},
                "dataMapping": {"status": {"ABC": "CBA"}},
            }
        },
    )
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
