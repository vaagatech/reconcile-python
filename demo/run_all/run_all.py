from __future__ import annotations

import asyncio
import importlib.util
import sys
import time
from pathlib import Path

from snapline.core import write_test_report
from snapline.demo_shared import (
    close_demo_database,
    create_demo_database,
    create_mock_server,
    resolve_report_config,
)

SCENARIO_IDS = [
    "reconcile-ignore-fields",
    "reconcile-transformations",
    "db-vs-db-sqlite",
    "reconcile-data-mapping-function",
    "db-comparison-transformations",
    "reconcile-combined-options",
    "api-vs-file-rest",
    "api-vs-file-graphql",
    "api-vs-file-soap",
    "api-vs-db-rest",
    "api-vs-db-graphql",
    "api-vs-db-soap",
    "db-vs-api-rest",
    "db-vs-api-graphql",
    "db-vs-api-soap",
]


def _load_scenario(scenario_id: str):
    scenario_path = Path(__file__).resolve().parent.parent / "scenarios" / scenario_id / "scenario.py"
    spec = importlib.util.spec_from_file_location(f"scenario_{scenario_id}", scenario_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load scenario: {scenario_id}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.scenario


async def main() -> int:
    print("═══════════════════════════════════════════════════════")
    print("  Snapline — Full Integration Demo (Python)")
    print("═══════════════════════════════════════════════════════")
    print("  Projects: 15 scenario workspaces under python/demo/scenarios/")
    print("  Modes: API↔file · DB↔DB · API↔DB · DB↔API")
    print("  Protocols: REST · GraphQL · SOAP · SQLite · OAuth2")
    print("  Pipeline: ignoreFields · transformations · dataMapping")
    print("  Reports: json · html · text (via REPORT_FORMAT env or CLI flags)")
    print("  Built by VaagaTech — https://www.vaagatech.com")
    print("═══════════════════════════════════════════════════════")

    server_handle = create_mock_server()
    print(f"\nMock API + GraphQL server listening at {server_handle.base_url}")

    database = create_demo_database()
    report_config = resolve_report_config()
    started_at = time.time() * 1000

    from snapline.demo_shared.types import ScenarioContext

    context = ScenarioContext(base_url=server_handle.base_url, database=database)

    try:
        results = []
        for scenario_id in SCENARIO_IDS:
            scenario = _load_scenario(scenario_id)
            results.append(await scenario.run(context))

        duration_ms = int(time.time() * 1000 - started_at)
        passed = sum(1 for result in results if result["passed"])
        failed = len(results) - passed

        print("───────────────────────────────────────────────────────")
        print(f"  Summary: {passed} passed, {failed} failed ({duration_ms}ms)")
        print("───────────────────────────────────────────────────────")

        if report_config:
            report_path = write_test_report(
                results,
                report_config,
                {
                    "durationMs": duration_ms,
                    "environment": {
                        "baseUrl": server_handle.base_url,
                        "reportFormat": report_config["format"],
                    },
                },
            )
            print(f"\nReport written to {report_path}")
            print("Upload this artifact to your CI dashboard or reporting system.")

        return 1 if failed > 0 else 0
    finally:
        close_demo_database(database)
        server_handle.server.shutdown()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
