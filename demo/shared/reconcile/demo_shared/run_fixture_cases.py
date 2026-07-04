from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from reconcile.core import (
    api,
    assert_against_file,
    execute_api,
    load_json_file,
    to_api_request_config,
)
from reconcile.auth_adapters import AuthAdapter

from .types import ScenarioModule


def _read_case_meta(case_dir: Path) -> dict[str, Any]:
    return load_json_file(case_dir / "case.json")


def _resolve_preset(value: Any, presets: dict[str, Any] | None) -> Any:
    if isinstance(value, str) and presets:
        return presets.get(value)
    if isinstance(value, dict):
        return value
    return None


def _discover_case_ids(cases_root: Path) -> list[str]:
    return sorted(path.name for path in cases_root.iterdir() if path.is_dir())


def _build_api_config(case_dir: Path, meta: dict[str, Any], defaults: dict[str, Any]) -> dict[str, Any]:
    protocol = meta.get("protocol") or defaults.get("protocol", "graphql")
    endpoint = meta.get("endpoint") or defaults.get("endpoint", "/graphql")
    data_path = meta.get("dataPath") or defaults.get("dataPath")

    if protocol == "graphql":
        return {
            **api.graphql(
                {
                    "endpoint": endpoint,
                    "queryFile": str(case_dir / "query.graphql"),
                    "variablesFile": str(case_dir / "variables.json"),
                    "dataPath": data_path,
                }
            )
        }

    if protocol == "soap":
        return {
            **api.soap(
                {
                    "endpoint": endpoint,
                    "soapAction": meta.get("soapAction", "GetUser"),
                    "inputFile": str(case_dir / "input.xml"),
                }
            )
        }

    return {
        "endpoint": endpoint,
        "method": meta.get("method", "GET"),
        "protocol": "rest",
        "inputFile": str(case_dir / "input.json")
        if (case_dir / "input.json").exists()
        else None,
    }


def _log_case_result(
    case_name: str,
    passed: bool,
    expect_match: bool,
    match: bool,
    diff: Any,
    failure_type: str | None = None,
) -> None:
    if passed:
        suffix = ""
        if failure_type == "auth":
            suffix = " (expected HTTP 401)"
        elif not expect_match:
            suffix = " (expected mismatch)"
        print(f"  ✓ {case_name}{suffix}")
        return

    print(f"  ✗ {case_name}")
    print(f"    expected match={expect_match}, got match={match}")
    if diff:
        print(f"    diff: {json.dumps(diff)}")


async def run_api_fixture_cases(options: dict[str, Any]) -> dict[str, Any]:
    suite_name = options["suiteName"]
    fixtures_root = Path(options["fixturesRoot"])
    base_url = options["baseUrl"]
    auth: AuthAdapter | None = options.get("auth")
    defaults = options.get("defaults", {})
    presets = options.get("presets", {})
    case_ids = options.get("caseIds")

    cases_root = fixtures_root / "cases"
    ids = case_ids or _discover_case_ids(cases_root)
    results: list[dict[str, Any]] = []
    passed = True

    print(f"\n▶ {suite_name}")

    auth_headers = dict(options.get("authHeaders") or {})
    if auth:
        auth_result = await auth.initialize()
        auth_headers = auth_result["headers"]
        results.append(
            {
                "step": "auth",
                "passed": True,
                "token": "[redacted]" if auth_result.get("token") else None,
            }
        )
        print("  ✓ auth initialized")

    for case_id in ids:
        case_dir = cases_root / case_id
        meta = _read_case_meta(case_dir)
        expect_match = meta["expectMatch"]
        expected_status = meta.get("expectStatus", 200)
        api_config = _build_api_config(case_dir, meta, defaults)
        request = to_api_request_config(api_config)
        case_auth_headers = {} if meta.get("skipAuth") else auth_headers
        response = execute_api(request, {"baseUrl": base_url, "authHeaders": case_auth_headers})

        if response["status"] != expected_status:
            passed = False
            results.append(
                {
                    "step": case_id,
                    "passed": False,
                    "message": f"Expected HTTP {expected_status}, got {response['status']}",
                    "data": response["data"],
                }
            )
            print(f"  ✗ {meta['name']}")
            print(f"    HTTP {response['status']}")
            continue

        if expected_status != 200:
            case_passed = not expect_match
            if not case_passed:
                passed = False
            results.append(
                {
                    "step": case_id,
                    "passed": case_passed,
                    "message": meta.get("failureType"),
                    "data": response["data"],
                }
            )
            _log_case_result(
                meta["name"],
                case_passed,
                expect_match,
                False,
                None,
                meta.get("failureType"),
            )
            continue

        reconcile_options = {
            "ignoreFields": meta.get("ignoreFields") or defaults.get("ignoreFields"),
            "transformations": (
                _resolve_preset(meta.get("transformations"), presets.get("transformations"))
                or meta.get("transformations")
                or defaults.get("transformations")
            ),
            "dataMapping": (
                _resolve_preset(meta.get("dataMapping"), presets.get("dataMapping"))
                or meta.get("dataMapping")
                or defaults.get("dataMapping")
            ),
        }

        assertion = assert_against_file(
            response["data"],
            case_dir / "expected.json",
            reconcile_options,
        )
        case_passed = assertion["match"] == expect_match

        if meta.get("expectedDiffPath") and not expect_match:
            diff_path = (assertion.get("diff") or {}).get("path", "")
            if not diff_path.startswith(meta["expectedDiffPath"]):
                passed = False
                results.append(
                    {
                        "step": case_id,
                        "passed": False,
                        "message": (
                            f"Expected diff at \"{meta['expectedDiffPath']}\", "
                            f"got \"{diff_path or '(none)'}\""
                        ),
                        "diff": assertion.get("diff"),
                        "processed": assertion.get("processed"),
                    }
                )
                _log_case_result(meta["name"], False, expect_match, assertion["match"], assertion.get("diff"))
                continue

        if not case_passed:
            passed = False

        results.append(
            {
                "step": case_id,
                "passed": case_passed,
                "diff": assertion.get("diff"),
                "processed": assertion.get("processed"),
                "message": meta.get("failureType"),
            }
        )
        _log_case_result(
            meta["name"],
            case_passed,
            expect_match,
            assertion["match"],
            None if case_passed else assertion.get("diff"),
        )

    summary = "PASSED" if passed else "FAILED"
    print(f"\n{'✅' if passed else '❌'} {suite_name}: {summary}\n")
    return {"name": suite_name, "passed": passed, "results": results}


async def run_reconcile_fixture_cases(options: dict[str, Any]) -> dict[str, Any]:
    suite_name = options["suiteName"]
    fixtures_root = Path(options["fixturesRoot"])
    presets = options.get("presets", {})
    case_ids = options.get("caseIds")

    cases_root = fixtures_root / "cases"
    ids = case_ids or _discover_case_ids(cases_root)
    results: list[dict[str, Any]] = []
    passed = True

    print(f"\n▶ {suite_name}")

    for case_id in ids:
        case_dir = cases_root / case_id
        meta = _read_case_meta(case_dir)
        live_data = load_json_file(case_dir / "live.json")
        reconcile_options = {
            "ignoreFields": meta.get("ignoreFields"),
            "transformations": (
                _resolve_preset(meta.get("transformations"), presets.get("transformations"))
                or meta.get("transformations")
            ),
            "dataMapping": (
                _resolve_preset(meta.get("dataMapping"), presets.get("dataMapping"))
                or meta.get("dataMapping")
            ),
        }

        assertion = assert_against_file(
            live_data,
            case_dir / "expected.json",
            reconcile_options,
        )
        case_passed = assertion["match"] == meta["expectMatch"]

        if meta.get("expectedDiffPath") and not meta["expectMatch"]:
            diff_path = (assertion.get("diff") or {}).get("path", "")
            if not diff_path.startswith(meta["expectedDiffPath"]):
                passed = False
                results.append(
                    {
                        "step": case_id,
                        "passed": False,
                        "message": (
                            f"Expected diff at \"{meta['expectedDiffPath']}\", "
                            f"got \"{diff_path or '(none)'}\""
                        ),
                        "diff": assertion.get("diff"),
                    }
                )
                _log_case_result(meta["name"], False, meta["expectMatch"], assertion["match"], assertion.get("diff"))
                continue

        if not case_passed:
            passed = False

        results.append(
            {
                "step": case_id,
                "passed": case_passed,
                "diff": assertion.get("diff"),
                "processed": assertion.get("processed"),
                "message": meta.get("failureType"),
            }
        )
        _log_case_result(
            meta["name"],
            case_passed,
            meta["expectMatch"],
            assertion["match"],
            None if case_passed else assertion.get("diff"),
        )

    summary = "PASSED" if passed else "FAILED"
    print(f"\n{'✅' if passed else '❌'} {suite_name}: {summary}\n")
    return {"name": suite_name, "passed": passed, "results": results}
