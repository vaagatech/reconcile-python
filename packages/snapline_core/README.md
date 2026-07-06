# snapline-core

Declarative test orchestration for Snapline — configure auth, API calls, and cross-system comparisons as data.

## Install

```bash
pip install snapline-core
```

## Quick start

```python
import asyncio
from snapline.core import auth, test_suite

async def main():
    result = await test_suite("My API test", {
        "baseUrl": "https://api.example.com",
        "auth": auth.oauth2({
            "tokenUrl": "https://api.example.com/oauth/token",
            "clientId": "client-id",
            "clientSecret": "client-secret",
        }),
        "api": {
            "endpoint": "/users/me",
            "method": "GET",
            "expectedFile": "fixtures/expected.json",
            "ignoreFields": ["traceId"],
        },
    })
    print(result)

asyncio.run(main())
```

## Documentation

Full docs, demos, and integration examples:

https://github.com/vaagatech/snapline-python
