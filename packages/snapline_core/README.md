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

## Database connections (`DbConnectionLike`)

Published `snapline-core` does **not** ship SQL drivers (runtime dependency: `httpx` only). Implement `DbConnectionLike` with your Postgres/MySQL client, or copy `examples/in_memory_db.py` for a minimal in-memory stub.

```python
from snapline.core.types import DbConnectionLike

class AppDb(DbConnectionLike):
    async def query(self, sql: str, params: dict | None = None) -> list[dict]:
        # your driver here
        return rows
```

Demos use `snapline.demo_shared` for SQLite and stub postgres/mysql (`create_sqlite_connection`, `seed_db`).

## Queue → poll (`publishAndPoll`)

Install `snapline-messaging-adapters` for queue publishers. Publish a message, then poll SQL or the filesystem for async results:

```python
from snapline.messaging_adapters import messaging
from snapline.core import run_publish_and_poll

queue = messaging.memory()

result = await run_publish_and_poll({
    "publish": {"publisher": queue["publisher"], "topic": "orders.request", "payload": {"orderId": "ORD-1"}},
    "poll": {"db": {"db": app_db, "query": "SELECT * FROM orders WHERE correlationId = :correlationId"}},
    "expected": {"orderId": "ORD-1", "status": "PROCESSED"},
})
```

See `examples/publish_and_poll_file.py` and the [Node.js docs](https://vaagatech.github.io/snapline/guide.html) for Kafka setup.

## Warehouse comparison (`run_warehouse_comparison`)

Chunked SQL → document-store consistency for data-warehouse ETL (26–30 tables in production). Streams a JSONL report so large datasets never load fully into memory.

```python
import asyncio
from snapline.core import nosql, run_warehouse_comparison

async def main():
    # source_db: your Postgres/MySQL client implementing DbConnectionLike
    class SourceDb:
        async def query(self, sql, params=None):
            return [{"customerId": "1", "email": "alice@example.com", "status": "ACTIVE"}]

    result = await run_warehouse_comparison({
        "suiteName": "Warehouse sync",
        "sourceDb": SourceDb(),
        "targetDb": nosql.memory(),  # production: MongoDB DocumentStoreLike adapter
        "tables": [{
            "id": "wh_customers",
            "sourceQuery": "SELECT customer_id AS customerId, email, status FROM wh_customers",
            "targetCollection": "customers",
            "linkKeys": {"customerId": "customerId"},
            "dataMapping": {"status": {"ACTIVE": "ACTV"}},
        }],
        "chunkSize": 100,
        "maxRowsPerTable": 10_000,
        "maxTotalRows": 50_000,
        "report": {"outputPath": "./reports/warehouse.jsonl", "format": "jsonl"},
    })

asyncio.run(main())
```

See demo `project-db` for a full SQLite → in-memory example via `snapline.demo_shared`.

### Snapline Hub (optional reporting UI)

Push test results to [Snapline Hub](https://vaagatech.github.io/snapline-hub/) for a centralized dashboard. Hub is **optional** — Snapline works fully without it.

```python
from snapline.core import build_report, push_test_report_to_hub, resolve_hub_config

report = build_report([result], {"durationMs": 1200})
push_test_report_to_hub(report, hub_url="http://localhost:3847")

# Or via env / CLI:
# SNAPLINE_HUB_URL=http://localhost:3847 uv run demo
hub_config = resolve_hub_config()
if hub_config:
    push_test_report_to_hub(report, config=hub_config)
```

See also: [Node.js edition](https://vaagatech.github.io/snapline/) · [Snapline Hub README](https://vaagatech.github.io/snapline-hub/#readme)

## Documentation

**https://vaagatech.github.io/snapline-python/**

- [Overview](https://vaagatech.github.io/snapline-python/)
- [End-to-end guide](https://vaagatech.github.io/snapline-python/guide.html)
- [Node.js edition](https://vaagatech.github.io/snapline/)
- [Snapline Hub](https://vaagatech.github.io/snapline-hub/) — optional reporting UI

Repository: https://github.com/vaagatech/snapline-python
