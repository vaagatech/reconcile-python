from __future__ import annotations

import asyncio
import importlib.util
import sys
import time
from pathlib import Path
from typing import Any

from snapline.core import build_report, push_test_report_to_hub, resolve_hub_config, resolve_report_config, write_test_report
from snapline.demo_shared import (
    apply_demo_env,
    close_demo_database,
    close_mock_server,
    create_demo_database,
    create_mock_server,
)
from snapline.demo_shared.types import ScenarioContext

from snapline.demo_shared.scenario_registry import DOCS_URL, SCENARIO_ORDER, validate_scenario_registry

SCENARIOS_DIR = Path(__file__).resolve().parent.parent / "scenarios"


def _load_scenario(scenario_id: str):
    scenario_dir = SCENARIOS_DIR / scenario_id
    scenario_path = scenario_dir / "scenario.py"
    module_name = f"scenario_{scenario_id.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(
        module_name,
        scenario_path,
        submodule_search_locations=[str(scenario_dir)],
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load scenario: {scenario_id}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module.scenario


def _scenario_report_path(scenario_id: str, report_format: str) -> str:
    extension = "txt" if report_format == "text" else report_format
    return f"./reports/scenarios/{scenario_id}.{extension}"


def _publish_scenario_reports(
    scenario_id: str,
    result: dict[str, Any],
    *,
    duration_ms: int,
    base_url: str,
    report_config: dict[str, Any] | None,
    hub_config: dict[str, Any] | None,
) -> None:
    if report_config:
        try:
            per_scenario_config = {
                **report_config,
                "outputPath": _scenario_report_path(scenario_id, report_config["format"]),
            }
            report_path = write_test_report(
                [result],
                per_scenario_config,
                {
                    "durationMs": duration_ms,
                    "environment": {"baseUrl": base_url, "scenarioId": scenario_id},
                },
            )
            print(f"  [file] {scenario_id} → {report_path}")
        except Exception as exc:
            print(f"  [file] {scenario_id} failed: {exc}")

    if hub_config:
        try:
            report = build_report(
                [result],
                {
                    "durationMs": duration_ms,
                    "environment": {"baseUrl": base_url, "scenarioId": scenario_id},
                },
            )
            tags = list({*(hub_config.get("tags") or []), "python", "demo", scenario_id})
            hub_result = push_test_report_to_hub(
                report,
                config={
                    **hub_config,
                    "label": result.get("name", scenario_id),
                    "project": scenario_id,
                    "tags": tags,
                },
            )
            print(f"  [hub]  {scenario_id} → {hub_result['url']}")
        except Exception as exc:
            print(f"  [hub]  {scenario_id} push failed: {exc}")


async def main() -> int:
    validate_scenario_registry(SCENARIOS_DIR)

    print("═══════════════════════════════════════════════════════")
    print("  Snapline — Full Integration Demo (Python)")
    print("═══════════════════════════════════════════════════════")
    print(f"  {len(SCENARIO_ORDER)} scenarios · uv run demo-list to browse")
    print("  uv run demo-run <id> to run one scenario from root")
    print(f"  Docs: {DOCS_URL}")
    print("═══════════════════════════════════════════════════════")

    server_handle = create_mock_server()
    print(f"\nMock API + GraphQL server listening at {server_handle.base_url}")

    database = create_demo_database()
    apply_demo_env(server_handle.base_url)
    report_config = resolve_report_config()
    hub_config = resolve_hub_config()
    started_at = time.time() * 1000

    context = ScenarioContext(base_url=server_handle.base_url, database=database)

    try:
        results = []
        for scenario_id in SCENARIO_ORDER:
            scenario_start = time.time() * 1000
            print(f"\n▶ {scenario_id}")
            scenario = _load_scenario(scenario_id)
            try:
                result = await scenario.run(context)
            except Exception as exc:
                result = {
                    "name": scenario.name,
                    "passed": False,
                    "results": [{"step": "run", "passed": False, "message": str(exc)}],
                }
            results.append(result)
            _publish_scenario_reports(
                scenario_id,
                result,
                duration_ms=int(time.time() * 1000 - scenario_start),
                base_url=server_handle.base_url,
                report_config=report_config,
                hub_config=hub_config,
            )

        duration_ms = int(time.time() * 1000 - started_at)
        passed = sum(1 for result in results if result["passed"])
        failed = len(results) - passed

        print("\n───────────────────────────────────────────────────────")
        print(f"  Summary: {passed} passed, {failed} failed ({duration_ms}ms)")
        print("───────────────────────────────────────────────────────")

        if report_config:
            try:
                report_path = write_test_report(
                    results,
                    report_config,
                    {
                        "durationMs": duration_ms,
                        "environment": {
                            "baseUrl": server_handle.base_url,
                            "reportFormat": report_config["format"],
                            "suiteName": "full-demo",
                        },
                    },
                )
                print(f"\n[file] Full demo summary → {report_path}")
            except Exception as exc:
                print(f"[file] Full demo summary failed: {exc}")

        return 1 if failed > 0 else 0
    finally:
        close_demo_database(database)
        close_mock_server(server_handle)


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
