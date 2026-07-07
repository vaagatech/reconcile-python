from __future__ import annotations

from typing import Any

from snapline.api_adapters import execute_api
from snapline.engine import snapline

from ..types import CrossSystemResult, DbToApiConfig


async def run_db_to_api(
    config: DbToApiConfig | dict[str, Any],
    auth_headers: dict[str, str] | None = None,
    base_url: str | None = None,
    fetch_impl: Any | None = None,
) -> CrossSystemResult:
    rows = await config["db"]["db"].query(
        config["db"]["query"],
        config["db"].get("params", {}),
    )
    db_data = rows[0] if rows else None

    api_config = dict(config["api"])
    expected_status = api_config.pop("expectedStatus", 200)
    input_from_db = config.get("inputFromDb", True)

    response = execute_api(
        api_config,
        {
            "baseUrl": base_url,
            "authHeaders": auth_headers or {},
            "fetchImpl": fetch_impl,
            "inputFromRow": db_data if input_from_db and db_data else None,
        },
    )

    if response["status"] != expected_status:
        return {
            "match": False,
            "source": db_data,
            "target": response["data"],
            "diff": {
                "path": "(http)",
                "actual": response["status"],
                "expected": expected_status,
                "message": f"Expected status {expected_status}, got {response['status']}",
            },
        }

    result = snapline(
        db_data,
        response["data"],
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
