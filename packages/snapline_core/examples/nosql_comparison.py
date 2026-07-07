"""NoSQL document store comparison example."""
import asyncio
import sys

from snapline.core import nosql, test_suite


async def main() -> int:
    source_store = nosql.memory()
    target_store = nosql.memory()

    nosql.seed(
        source_store,
        "customers",
        [
            {
                "customerId": "cust_1",
                "email": "alice@example.com",
                "status": "ACTIVE",
                "tier": "gold",
                "profile": {"role": "admin", "department": "engineering"},
            }
        ],
    )
    nosql.seed(
        target_store,
        "customer_snapshots",
        [
            {
                "customerId": "cust_1",
                "email": "alice@example.com",
                "status": "ACTIVE",
                "tier": "gold",
                "profile": {"role": "admin", "department": "engineering"},
            }
        ],
    )

    result = await test_suite(
        "NoSQL document sync",
        {
            "dbComparison": {
                "sourceDb": source_store,
                "targetDb": target_store,
                "sourceCollection": "customers",
                "targetCollection": "customer_snapshots",
                "sourceFilter": {"email": "alice@example.com"},
                "linkKeys": {"customerId": "customerId"},
            }
        },
    )
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
