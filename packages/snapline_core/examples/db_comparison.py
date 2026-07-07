import asyncio

from snapline.core import test_suite

from .in_memory_db import InMemoryDb


async def main() -> None:
    source_db = InMemoryDb([{"status": "ABC", "email": "alice@example.com"}])
    target_db = InMemoryDb([{"status": "CBA", "email": "alice@example.com"}])

    result = await test_suite(
        "DB Sync Check",
        {
            "dbComparison": {
                "sourceDb": source_db,
                "targetDb": target_db,
                "query": "SELECT status, email FROM users WHERE email = :email",
                "params": {"email": "alice@example.com"},
                "dataMapping": {"status": {"ABC": "CBA"}},
            }
        },
    )
    print(result)


asyncio.run(main())
