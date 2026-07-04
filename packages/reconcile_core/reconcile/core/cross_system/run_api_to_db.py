from __future__ import annotations

from typing import Any

from reconcile.api_adapters import execute_api
from reconcile.engine import reconcile

from ..types import ApiToDbConfig, CrossSystemResult


async def run_api_to_db(
    config: ApiToDbConfig | dict[str, Any],
    auth_headers: dict[str, str] | None = None,
    base_url: str | None = None,
    fetch_impl: Any | None = None,
) -> CrossSystemResult:
    api_config = dict(config["api"])
    expected_status = api_config.pop("expectedStatus", 200)

    response = execute_api(
        api_config,
        {
            "baseUrl": base_url,
            "authHeaders": auth_headers or {},
            "fetchImpl": fetch_impl,
        },
    )

    if response["status"] != expected_status:
        return {
            "match": False,
            "source": response["data"],
            "target": None,
            "diff": {
                "path": "(http)",
                "actual": response["status"],
                "expected": expected_status,
                "message": f"Expected status {expected_status}, got {response['status']}",
            },
        }

    rows = await config["db"]["db"].query(
        config["db"]["query"],
        config["db"].get("params", {}),
    )
    db_data = rows[0] if rows else None

    result = reconcile(
        response["data"],
        db_data,
        {
            "ignoreFields": config.get("ignoreFields", []),
            "transformations": config.get("transformations", {}),
            "dataMapping": config.get("dataMapping", {}),
        },
    )

    return {
        "match": result["match"],
        "source": result["processed"],
        "target": result["expected"],
        "diff": result["diff"],
    }
