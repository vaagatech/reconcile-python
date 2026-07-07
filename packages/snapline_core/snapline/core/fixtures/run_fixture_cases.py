from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from snapline.api_adapters import api, execute_api
from snapline.engine import assert_against_file, load_json_file
from snapline.engine.io.safe_path import assert_within_root

from ..api_config.to_api_request_config import to_api_request_config
from ..types import TestStepResult, TestSuiteResult
from .fixture_layout import case_file_path, resolve_fixture_layout
from .resolve_fixture_snapline_options import resolve_fixture_snapline_options
from .types import (
    FixtureCaseMeta,
    ResolvedFixtureLayout,
    RunApiFixtureCasesOptions,
    RunSnaplineFixtureCasesOptions,
)


def _read_case_meta(
    case_dir: Path,
    layout: ResolvedFixtureLayout,
    fixtures_root: Path,
) -> FixtureCaseMeta:
    meta_path = assert_within_root(
        fixtures_root,
        case_file_path(case_dir, layout["caseMetaFile"]),
    )
    return load_json_file(meta_path)


def _discover_case_ids(cases_root: Path, fixtures_root: Path) -> list[str]:
    resolved_cases_root = assert_within_root(fixtures_root, cases_root)
    return sorted(path.name for path in resolved_cases_root.iterdir() if path.is_dir())


def _exists(path: str | Path) -> bool:
    return Path(path).is_file()


def _safe_case_file(case_dir: Path, file_name: str, fixtures_root: Path) -> Path:
    return assert_within_root(fixtures_root, case_file_path(case_dir, file_name))


def _build_api_config(
    case_dir: Path,
    meta: FixtureCaseMeta,
    defaults: dict[str, Any],
    layout: ResolvedFixtureLayout,
    fixtures_root: Path,
) -> dict[str, Any]:
    protocol = meta.get("protocol") or defaults.get("protocol", "graphql")
    endpoint = meta.get("endpoint") or defaults.get("endpoint", "/graphql")
    data_path = meta.get("dataPath") or defaults.get("dataPath")

    if protocol == "graphql":
        return {
            **api.graphql(
                {
                    "endpoint": endpoint,
                    "queryFile": str(_safe_case_file(case_dir, layout["queryFile"], fixtures_root)),
                    "variablesFile": str(
                        _safe_case_file(case_dir, layout["variablesFile"], fixtures_root)
                    ),
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
                    "inputFile": str(_safe_case_file(case_dir, layout["soapInputFile"], fixtures_root)),
                }
            )
        }

    rest_input_path = _safe_case_file(case_dir, layout["restInputFile"], fixtures_root)
    return {
        "endpoint": endpoint,
        "method": meta.get("method", "GET"),
        "protocol": "rest",
        "inputFile": str(rest_input_path) if _exists(rest_input_path) else None,
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


def _api_execute_context(options: RunApiFixtureCasesOptions | dict[str, Any], auth_headers: dict[str, str]) -> dict[str, Any]:
    return {
        "baseUrl": options["baseUrl"],
        "authHeaders": auth_headers,
        "fetchImpl": options.get("fetchImpl"),
        "timeoutMs": options.get("timeoutMs"),
        "blockPrivateNetworks": options.get("blockPrivateNetworks", False),
        "blockMetadataHosts": options.get("blockMetadataHosts", True),
    }


async def run_api_fixture_cases(
    options: RunApiFixtureCasesOptions | dict[str, Any],
) -> TestSuiteResult:
    suite_name = options["suiteName"]
    fixtures_root = Path(options["fixturesRoot"]).resolve()
    base_url = options["baseUrl"]
    auth = options.get("auth")
    layout = options.get("layout")
    defaults = options.get("defaults") or {}
    presets = options.get("presets") or {}
    case_ids = options.get("caseIds")

    cases_dir = (layout or {}).get("casesDir", "cases")
    cases_root = fixtures_root / cases_dir
    ids = case_ids or _discover_case_ids(cases_root, fixtures_root)
    results: list[TestStepResult] = []
    passed = True

    print(f"\n▶ {suite_name}")

    auth_headers = dict(options.get("authHeaders") or {})
    if auth:
        try:
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
        except Exception as error:
            passed = False
            message = str(error)
            results.append({"step": "auth", "passed": False, "message": message})
            print(f"  ✗ auth failed: {message}")
            return {"name": suite_name, "passed": False, "results": results}

    for case_id in ids:
        case_dir = assert_within_root(fixtures_root, cases_root / case_id)
        base_layout = resolve_fixture_layout(layout, defaults)
        meta = _read_case_meta(case_dir, base_layout, fixtures_root)
        case_layout = resolve_fixture_layout(layout, defaults, meta)
        expect_match = meta["expectMatch"]
        expected_status = meta.get("expectStatus", 200)
        api_config = _build_api_config(case_dir, meta, defaults, case_layout, fixtures_root)
        request = to_api_request_config(api_config)
        case_auth_headers = {} if meta.get("skipAuth") else auth_headers
        execute_context = {
            **_api_execute_context(options, case_auth_headers),
            "authHeaders": case_auth_headers,
        }
        response = execute_api(request, execute_context)

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

        snapline_options = resolve_fixture_snapline_options(meta, defaults, presets)
        assertion = assert_against_file(
            response["data"],
            _safe_case_file(case_dir, case_layout["expectedFile"], fixtures_root),
            snapline_options,
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


async def run_snapline_fixture_cases(
    options: RunSnaplineFixtureCasesOptions | dict[str, Any],
) -> TestSuiteResult:
    suite_name = options["suiteName"]
    fixtures_root = Path(options["fixturesRoot"]).resolve()
    layout = options.get("layout")
    defaults = options.get("defaults")
    presets = options.get("presets") or {}
    case_ids = options.get("caseIds")

    cases_dir = (layout or {}).get("casesDir", "cases")
    cases_root = fixtures_root / cases_dir
    ids = case_ids or _discover_case_ids(cases_root, fixtures_root)
    results: list[TestStepResult] = []
    passed = True

    print(f"\n▶ {suite_name}")

    for case_id in ids:
        case_dir = assert_within_root(fixtures_root, cases_root / case_id)
        base_layout = resolve_fixture_layout(layout, defaults)
        meta = _read_case_meta(case_dir, base_layout, fixtures_root)
        case_layout = resolve_fixture_layout(layout, defaults, meta)
        live_data = load_json_file(_safe_case_file(case_dir, case_layout["liveFile"], fixtures_root))
        snapline_options = resolve_fixture_snapline_options(meta, defaults, presets)

        assertion = assert_against_file(
            live_data,
            _safe_case_file(case_dir, case_layout["expectedFile"], fixtures_root),
            snapline_options,
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
