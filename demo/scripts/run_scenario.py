#!/usr/bin/env python3
"""Run one demo scenario from the repo root with local mock API / SQLite when needed.

Usage:
  uv run demo-list
  uv run demo-run api-vs-file-graphql
"""
from __future__ import annotations

import argparse
import asyncio
import importlib.util
import sys
from pathlib import Path
from typing import List, Optional

from snapline.demo_shared import bootstrap_scenario

from snapline.demo_shared.scenario_registry import (
    DOCS_URL,
    NODE_DOCS_URL,
    SCENARIO_META,
    SCENARIO_ORDER,
    validate_scenario_registry,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SCENARIOS_DIR = REPO_ROOT / "demo" / "scenarios"


def print_list() -> None:
    print("Demo scenarios (uv run demo-run <id>):\n")
    for index, scenario_id in enumerate(SCENARIO_ORDER, start=1):
        meta = SCENARIO_META[scenario_id]
        flags = "+".join(
            part
            for part, enabled in (("api", meta["needs_server"]), ("db", meta["needs_database"]))
            if enabled
        )
        modes = ", ".join(meta["modes"])
        print(f"  {index:2}. {scenario_id:<32} [{flags or 'standalone'}] {modes}")
    print("\nRun all: uv run demo")
    print(f"\nDocumentation: {DOCS_URL}")
    print(f"Node.js docs:  {NODE_DOCS_URL}")


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


async def run_one(scenario_id: str) -> int:
    if scenario_id not in SCENARIO_META:
        print(f'Unknown scenario "{scenario_id}". Run: uv run demo-list', file=sys.stderr)
        return 1

    scenario = _load_scenario(scenario_id)
    return await bootstrap_scenario(scenario)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run Snapline demo scenarios")
    parser.add_argument("scenario_id", nargs="?", help="Scenario id to run")
    parser.add_argument("--list", "-l", action="store_true", help="List scenarios")
    args = parser.parse_args(argv)

    if args.list or not args.scenario_id:
        print_list()
        return 0

    return asyncio.run(run_one(args.scenario_id))


if __name__ == "__main__":
    validate_scenario_registry(SCENARIOS_DIR)
    raise SystemExit(main())
