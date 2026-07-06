# Snapline (Python)

Declarative Snapshot and Reconciliation Testing for Python.

## Install

```bash
cd python
pip install -e packages/snapline_engine
pip install -e packages/snapline_api_adapters
pip install -e packages/snapline_auth_adapters
pip install -e packages/snapline_core
pip install -e demo/shared
```

Or with uv:

```bash
cd python
uv sync
```

## Run the full integration demo (19 scenarios)

```bash
cd reconcile-python
uv sync

uv run demo              # build not required — run all 19 scenarios
uv run demo-list         # list scenario ids
uv run demo-run api-vs-file-graphql   # one scenario (mock API/DB auto-started)
python run_demo.py       # alternative entry point
```

Optional report output:

```bash
REPORT_FORMAT=html REPORT_OUTPUT=reports/demo.html uv run demo
```

## Packages

| Pip package | Python import |
|---|---|
| `snapline-engine` | `snapline.engine` |
| `snapline-api-adapters` | `snapline.api_adapters` |
| `snapline-auth-adapters` | `snapline.auth_adapters` |
| `snapline-core` | `snapline.core` |
| `snapline-demo-shared` | `snapline.demo_shared` |

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

## Feature parity

- Snapline pipeline: `ignoreFields` → `transformations` → `dataMapping` → deep compare
- Test modes: API↔file, DB↔DB, API↔DB, DB↔API in one `test_suite`
- Protocols: REST, GraphQL, SOAP
- Auth: Basic, OAuth2 client credentials, OpenID (token/idToken/assertion)
- DB: real SQLite + stub postgres/mysql with `seed_db`
- NoSQL: in-memory document stores with `linkKeys`
- Reporting: JSON, HTML, text
- 19 integration demo scenarios with mock server and fixture cases
