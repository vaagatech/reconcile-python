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
from snapline.demo_shared.types import ScenarioContext

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from scenario_registry import SCENARIO_ORDER, validate_scenario_registry

SCENARIOS_DIR = Path(__file__).resolve().parent.parent / "scenarios"


def _load_scenario(scenario_id: str):
    scenario_path = SCENARIOS_DIR / scenario_id / "scenario.py"
    spec = importlib.util.spec_from_file_location(f"scenario_{scenario_id}", scenario_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load scenario: {scenario_id}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.scenario


async def main() -> int:
    validate_scenario_registry(SCENARIOS_DIR)

    print("═══════════════════════════════════════════════════════")
    print("  Snapline — Full Integration Demo (Python)")
    print("═══════════════════════════════════════════════════════")
    print(f"  {len(SCENARIO_ORDER)} scenarios · uv run demo-list to browse")
    print("  uv run demo-run <id> to run one scenario from root")
    print("═══════════════════════════════════════════════════════")

    server_handle = create_mock_server()
    print(f"\nMock API + GraphQL server listening at {server_handle.base_url}")

    database = create_demo_database()
    report_config = resolve_report_config()
    started_at = time.time() * 1000

    context = ScenarioContext(base_url=server_handle.base_url, database=database)

    try:
        results = []
        for scenario_id in SCENARIO_ORDER:
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

        return 1 if failed > 0 else 0
    finally:
        close_demo_database(database)
        server_handle.server.shutdown()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
