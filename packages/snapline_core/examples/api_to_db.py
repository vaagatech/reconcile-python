"""API vs database reconciliation example."""
import asyncio

from snapline.core import api, test_suite

from .in_memory_db import InMemoryDb


async def main() -> None:
    app_db = InMemoryDb([{"email": "alice@example.com", "status": "SYNCED"}])

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
                    "db": app_db,
                    "query": "SELECT email, status FROM users WHERE email = :email",
                    "params": {"email": "alice@example.com"},
                },
            },
        },
    )


if __name__ == "__main__":
    asyncio.run(main())
