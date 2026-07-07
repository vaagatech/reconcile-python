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

## Fixture-case runners

```python
import asyncio
from snapline.core import fixtures_dir, run_api_fixture_cases, resolve_report_config, write_test_report

async def main():
    result = await run_api_fixture_cases({
        "suiteName": "Customer account — GraphQL fixture cases",
        "fixturesRoot": str(fixtures_dir(__file__, {"relativePath": "fixtures"})),
        "baseUrl": "https://api.example.com",
        "defaults": {
            "endpoint": "/graphql",
            "protocol": "graphql",
            "dataPath": "customerAccount",
            "ignoreFields": ["metadata.traceId"],
        },
    })

    report_config = resolve_report_config({"defaultOutputPath": "./reports/run.json"})
    if report_config:
        write_test_report([result], report_config)

asyncio.run(main())
```

## Documentation

Full docs, demos, and integration examples:

https://github.com/vaagatech/snapline-python
