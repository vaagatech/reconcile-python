from __future__ import annotations

import os

from snapline.core import run_warehouse_comparison
from snapline.demo_shared.types import ScenarioContext

from .warehouse_seed import seed_warehouse_demo
from .warehouse_table_manifest import warehouse_tables


def _read_int_env(name: str, fallback: int) -> int:
    raw = os.environ.get(name)
    if not raw:
        return fallback
    try:
        parsed = int(raw, 10)
    except ValueError:
        return fallback
    return parsed if parsed > 0 else fallback


class Scenario:
    name = "Project DB — SQL warehouse → NoSQL consistency (streamed)"
    needs_server = False
    needs_database = False

    async def run(self, context: ScenarioContext) -> dict:
        seed = seed_warehouse_demo()
        try:
            redact = os.environ.get("WAREHOUSE_REDACT_FIELDS")
            return await run_warehouse_comparison(
                {
                    "suiteName": self.name,
                    "sourceDb": seed.source_db,
                    "targetDb": seed.target_db,
                    "tables": warehouse_tables,
                    "chunkSize": _read_int_env("WAREHOUSE_CHUNK_SIZE", 50),
                    "maxRowsPerTable": _read_int_env("WAREHOUSE_MAX_ROWS_PER_TABLE", 10_000),
                    "maxTotalRows": _read_int_env("WAREHOUSE_MAX_TOTAL_ROWS", 50_000),
                    "report": {
                        "outputPath": os.environ.get(
                            "WAREHOUSE_REPORT_PATH", "./reports/warehouse-stream.jsonl"
                        ),
                        "format": "jsonl",
                        "redactFields": redact.split(",") if redact else None,
                    },
                }
            )
        finally:
            seed.cleanup()


scenario = Scenario()
