"""GraphQL API vs fixture file example."""
import asyncio

from snapline.core import api, test_suite


async def main() -> None:
    await test_suite(
        "GraphQL snapshot",
        {
            "baseUrl": "https://api.example.com",
            "api": {
                **api.graphql(
                    {
                        "endpoint": "/graphql",
                        "query": "query($email: String!) { user(email: $email) { email status } }",
                        "variables": {"email": "alice@example.com"},
                        "dataPath": "user",
                    }
                ),
                "expectedFile": "./fixtures/user-expected.json",
            },
        },
    )


if __name__ == "__main__":
    asyncio.run(main())
