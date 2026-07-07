"""Database vs API reconciliation example."""
import asyncio

from snapline.core import api, db, seed_db, test_suite


async def main() -> None:
    seed_db(
        "postgresql://localhost:5432/app",
        [{"email": "alice@example.com", "status": "SYNCED", "role": "member"}],
    )

    await test_suite(
        "Database matches API",
        {
            "baseUrl": "https://api.example.com",
            "dbToApi": {
                "db": {
                    "db": db.postgres("postgresql://localhost:5432/app"),
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
