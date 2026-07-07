"""SOAP API vs fixture file example."""
import asyncio

from snapline.core import api, test_suite


async def main() -> None:
    await test_suite(
        "SOAP snapshot",
        {
            "baseUrl": "https://api.example.com",
            "api": {
                **api.soap(
                    {
                        "endpoint": "/soap/user",
                        "soapAction": "GetUser",
                        "inputFile": "./fixtures/get-user.xml",
                    }
                ),
                "expectedFile": "./fixtures/user-expected.json",
            },
        },
    )


if __name__ == "__main__":
    asyncio.run(main())
