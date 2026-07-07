"""Basic auth adapter example."""
import asyncio
import os

from snapline.auth_adapters import auth


async def main() -> None:
    adapter = auth.basic(
        {
            "username": os.environ.get("API_USERNAME", "demo-user"),
            "password": os.environ.get("API_PASSWORD", "demo-password"),
        }
    )

    auth_result = await adapter.initialize()
    print("Authorization header set:", bool(auth_result["headers"].get("Authorization")))
    print("Token available:", bool(auth_result.get("token")))


if __name__ == "__main__":
    asyncio.run(main())
