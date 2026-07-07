"""API vs database reconciliation example."""
import asyncio

from snapline.core import api, db, seed_db, test_suite


async def main() -> None:
    seed_db(
        "postgresql://localhost:5432/app",
        [{"email": "alice@example.com", "status": "SYNCED"}],
    )

    await test_suite(
        "API matches database",
        {
            "baseUrl": "https://api.example.com",
            "apiToDb": {
                "api": api.rest(
                    {
                        "endpoint": "/users/profile?email=alice@example.com",
                        "method": "GET",
                    }
                ),
                "db": {
                    "db": db.postgres("postgresql://localhost:5432/app"),
                    "query": "SELECT email, status FROM users WHERE email = :email",
                    "params": {"email": "alice@example.com"},
                },
            },
        },
    )


if __name__ == "__main__":
    asyncio.run(main())
