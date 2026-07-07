from __future__ import annotations

import os
import time

from snapline.core import resolve_report_config, write_test_report

from .mock_server import close_mock_server, create_mock_server
from .sqlite_setup import close_demo_database, create_demo_database
from .types import ScenarioContext, ScenarioModule


def apply_demo_env(base_url: str) -> None:
    os.environ["API_BASE_URL"] = base_url
    os.environ.setdefault("CLIENT_ID", "demo-client")
    os.environ.setdefault("CLIENT_SECRET", "demo-secret")


async def bootstrap_scenario(scenario: ScenarioModule) -> int:
    report_config = resolve_report_config()
    started_at = time.time() * 1000

    server_handle = None
    database = None

    try:
        if scenario.needs_server:
            server_handle = create_mock_server()
            print(f"Mock API + GraphQL server listening at {server_handle.base_url}")
            apply_demo_env(server_handle.base_url)

        if scenario.needs_database:
            database = create_demo_database()

        context = ScenarioContext(
            base_url=os.environ.get("API_BASE_URL", "http://127.0.0.1:0"),
            database=database,
        )

        try:
            result = await scenario.run(context)
        except Exception as exc:
            result = {
                "name": scenario.name,
                "passed": False,
                "results": [{"step": "run", "passed": False, "message": str(exc)}],
            }

        duration_ms = int(time.time() * 1000 - started_at)

        if report_config:
            report_path = write_test_report(
                [result],
                report_config,
                {
                    "durationMs": duration_ms,
                    "environment": {
                        "scenario": scenario.name,
                        "reportFormat": report_config["format"],
                    },
                },
            )
            print(f"Report written to {report_path}")

        return 0 if result["passed"] else 1
    finally:
        if database:
            close_demo_database(database)
        if server_handle:
            close_mock_server(server_handle)
