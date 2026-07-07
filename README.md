# Snapline (Python)

[![docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://vaagatech.github.io/snapline-python/)

Declarative Snapshot and Reconciliation Testing for Python — an open-source product by [VaagaTech](https://www.vaagatech.com) ([www.vaagatech.com](https://www.vaagatech.com)).

📖 **[Full documentation (GitHub Pages)](https://vaagatech.github.io/snapline-python/)** · [Node.js edition](https://vaagatech.github.io/snapline/)

| Page | Description |
|------|-------------|
| [Overview](https://vaagatech.github.io/snapline-python/) | Purpose, install, quick example |
| [Architecture](https://vaagatech.github.io/snapline-python/architecture.html) | Packages, Node parity, repo layout |
| [Getting Started](https://vaagatech.github.io/snapline-python/getting-started.html) | 5-minute setup |
| [End-to-End Guide](https://vaagatech.github.io/snapline-python/guide.html) | Complete usage workflow |
| [Demo Scenarios](https://vaagatech.github.io/snapline-python/demos.html) | 21 integration scenarios |
| [API Reference](https://vaagatech.github.io/snapline-python/reference.html) | Exports and config |

## Install

```bash
cd snapline-python
pip install -e packages/snapline_engine
pip install -e packages/snapline_api_adapters
pip install -e packages/snapline_auth_adapters
pip install -e packages/snapline_core
pip install -e demo/shared
```

Or with uv:

```bash
cd snapline-python
uv sync
```

## Run the full integration demo (21 scenarios)

```bash
cd snapline-python
uv sync

uv run demo              # run all 21 scenarios
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

`snapline-core` exports the same consumer utilities as `@vaagatech/snapline-core`:

- `test_suite`, `fixtures_dir`, `module_dir`
- `run_api_fixture_cases`, `run_snapline_fixture_cases`
- `resolve_report_config`, `write_test_report`
- `reconcile`, `snapline`, `DbConnectionLike`, NoSQL helpers

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
- DB: implement `DbConnectionLike` with your Postgres/MySQL driver (demos use `snapline.demo_shared` for SQLite stubs)
- NoSQL: in-memory document stores with `linkKeys`
- Reporting: JSON, HTML, text, streamed JSONL (`create_stream_report_writer`)
- Warehouse: `run_warehouse_comparison` for chunked SQL→NoSQL consistency
- Fixture-case runners: `run_api_fixture_cases`, `run_snapline_fixture_cases`
- 21 integration demo scenarios with mock server and fixture cases (same IDs as Node.js)
