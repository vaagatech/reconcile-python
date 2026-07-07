"""Database vs API reconciliation example."""
import asyncio

from snapline.core import api, test_suite

from .in_memory_db import InMemoryDb


async def main() -> None:
    app_db = InMemoryDb(
        [{"email": "alice@example.com", "status": "SYNCED", "role": "member"}]
    )

    await test_suite(
        "Database matches API",
        {
            "baseUrl": "https://api.example.com",
            "dbToApi": {
                "db": {
                    "db": app_db,
                    "query": "SELECT email, status, role FROM users WHERE email = :email",
                    "params": {"email": "alice@example.com"},
                },
                "api": api.rest({"endpoint": "/users/profile", "method": "GET"}),
                "inputFromDb": True,
            },
        },
    )


if __name__ == "__main__":
    asyncio.run(main())
