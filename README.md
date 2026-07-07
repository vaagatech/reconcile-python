# Snapline (Python)

Declarative Snapshot and Reconciliation Testing for Python.

📖 **[Full documentation (GitHub Pages)](https://vaagatech.github.io/snapline-python/)**

| Page | Description |
|------|-------------|
| [Overview](https://vaagatech.github.io/snapline-python/) | Purpose, install, quick example |
| [Architecture](https://vaagatech.github.io/snapline-python/architecture.html) | Packages, Node parity, repo layout |
| [Getting Started](https://vaagatech.github.io/snapline-python/getting-started.html) | 5-minute setup |
| [End-to-End Guide](https://vaagatech.github.io/snapline-python/guide.html) | Complete usage workflow |
| [Demo Scenarios](https://vaagatech.github.io/snapline-python/demos.html) | 19 integration scenarios |
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

## Run the full integration demo (19 scenarios)

```bash
cd snapline-python
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

`snapline-core` exports the same consumer utilities as `@vaagatech/snapline-core`:

- `test_suite`, `fixtures_dir`, `module_dir`
- `run_api_fixture_cases`, `run_snapline_fixture_cases`
- `resolve_report_config`, `write_test_report`
- `reconcile`, `snapline`, DB/NoSQL helpers

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
- Fixture-case runners: `run_api_fixture_cases`, `run_snapline_fixture_cases`
- 19 integration demo scenarios with mock server and fixture cases (same IDs as Node.js)
