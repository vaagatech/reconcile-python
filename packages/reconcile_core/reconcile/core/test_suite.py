from __future__ import annotations

import json
from typing import Any

from reconcile.api_adapters import execute_api
from reconcile.engine import assert_against_file

from .api_config.to_api_request_config import to_api_request_config
from .cross_system.run_api_to_db import run_api_to_db
from .cross_system.run_db_to_api import run_db_to_api
from .db_comparison.run_db_comparison import run_db_comparison
from .types import TestStepResult, TestSuiteConfig, TestSuiteResult


def _log_step_result(
    label: str,
    match: bool,
    diff: Any,
    on_fail,
) -> None:
    if match:
        print(f"  ✓ {label}")
    else:
        on_fail()
        print(f"  ✗ {label}")
        print(f"    diff: {json.dumps(diff)}")


async def test_suite(name: str, config: TestSuiteConfig | dict[str, Any]) -> TestSuiteResult:
    auth_adapter = config.get("auth")
    api = config.get("api")
    db_comparison = config.get("dbComparison")
    api_to_db = config.get("apiToDb")
    db_to_api = config.get("dbToApi")
    base_url = config.get("baseUrl")
    fetch_impl = config.get("fetchImpl")

    results: list[TestStepResult] = []
    passed = True

    def fail() -> None:
        nonlocal passed
        passed = False

    print(f"\n▶ {name}")

    auth_headers: dict[str, str] = {}
    if auth_adapter:
        auth_result = await auth_adapter.initialize()
        auth_headers = auth_result["headers"]
        results.append(
            {
                "step": "auth",
                "passed": True,
                "token": "[redacted]" if auth_result.get("token") else None,
            }
        )
        print("  ✓ auth initialized")

    if api:
        expected_file = api.get("expectedFile")
        ignore_fields = api.get("ignoreFields", [])
        transformations = api.get("transformations", {})
        data_mapping = api.get("dataMapping", {})
        expected_status = api.get("expectedStatus", 200)

        api_request = to_api_request_config(api)
        response = execute_api(
            api_request,
            {
                "baseUrl": base_url,
                "authHeaders": auth_headers,
                "fetchImpl": fetch_impl,
            },
        )

        if response["status"] != expected_status:
            fail()
            results.append(
                {
                    "step": "api",
                    "passed": False,
                    "message": f"Expected status {expected_status}, got {response['status']}",
                    "data": response["data"],
                }
            )
            print(
                f"  ✗ api status mismatch (expected {expected_status}, got {response['status']})"
            )
        elif expected_file:
            assertion = assert_against_file(
                response["data"],
                expected_file,
                {
                    "ignoreFields": ignore_fields,
                    "transformations": transformations,
                    "dataMapping": data_mapping,
                },
            )
            results.append(
                {
                    "step": "api-file",
                    "passed": assertion["match"],
                    "diff": assertion["diff"],
                    "processed": assertion["processed"],
                }
            )
            _log_step_result(
                "api response reconciled with fixture file",
                assertion["match"],
                assertion["diff"],
                fail,
            )
        else:
            results.append({"step": "api", "passed": True, "data": response["data"]})
            print("  ✓ api request completed")

    if db_comparison:
        db_result = await run_db_comparison(db_comparison)
        results.append({"step": "db-to-db", "passed": db_result["match"], **db_result})
        _log_step_result("db-to-db reconciliation passed", db_result["match"], db_result["diff"], fail)

    if api_to_db:
        result = await run_api_to_db(api_to_db, auth_headers, base_url, fetch_impl)
        results.append({"step": "api-to-db", "passed": result["match"], **result})
        _log_step_result("api-to-db reconciliation passed", result["match"], result["diff"], fail)

    if db_to_api:
        result = await run_db_to_api(db_to_api, auth_headers, base_url, fetch_impl)
        results.append({"step": "db-to-api", "passed": result["match"], **result})
        _log_step_result("db-to-api reconciliation passed", result["match"], result["diff"], fail)

    summary = "PASSED" if passed else "FAILED"
    print(f"\n{'✅' if passed else '❌'} {name}: {summary}\n")

    return {"name": name, "passed": passed, "results": results}
