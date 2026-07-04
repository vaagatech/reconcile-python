from __future__ import annotations

import os
import time

from snapline.core import auth, write_test_report

from .mock_server import create_mock_server
from .report_config import resolve_report_config
from .sqlite_setup import close_demo_database, create_demo_database
from .types import ScenarioContext, ScenarioModule


def create_demo_auth(base_url: str):
    return auth.oauth2(
        {
            "tokenUrl": f"{base_url}/oauth/token",
            "clientId": os.environ.get("CLIENT_ID", "demo-client"),
            "clientSecret": os.environ.get("CLIENT_SECRET", "demo-secret"),
        }
    )


async def bootstrap_scenario(scenario: ScenarioModule) -> int:
    report_config = resolve_report_config()
    started_at = time.time() * 1000

    server_handle = None
    database = None

    try:
        if scenario.needs_server:
            server_handle = create_mock_server()
            print(f"Mock API + GraphQL server listening at {server_handle.base_url}")

        if scenario.needs_database:
            database = create_demo_database()

        context = ScenarioContext(
            base_url=server_handle.base_url if server_handle else "http://127.0.0.1:0",
            database=database or create_demo_database(),
        )
        result = await scenario.run(context)

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
            server_handle.server.shutdown()
