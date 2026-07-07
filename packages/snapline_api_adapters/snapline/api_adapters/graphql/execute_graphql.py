from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from snapline.engine import load_json_file

from ..http_client import fetch_with_timeout
from ..resolve_url import resolve_url
from ..types import ApiExecuteContext, ApiExecuteResult, GraphqlApiConfig


def _load_query(config: GraphqlApiConfig) -> str:
    if config.get("query"):
        return config["query"]

    query_file = config.get("queryFile")
    if not query_file:
        return ""

    raw = Path(query_file).read_text(encoding="utf-8").strip()
    if raw.startswith("{"):
        parsed = json.loads(raw)
        return parsed.get("query", raw)
    return raw


def _get_by_path(obj: Any, path: str | None) -> Any:
    if not path:
        return obj

    cursor = obj
    for key in path.split("."):
        if isinstance(cursor, dict) and key in cursor:
            cursor = cursor[key]
        else:
            return None
    return cursor


def execute_graphql(
    config: GraphqlApiConfig,
    context: ApiExecuteContext | dict[str, Any] | None = None,
) -> ApiExecuteResult:
    ctx = context or {}
    base_url = ctx.get("baseUrl")
    auth_headers = ctx.get("authHeaders", {})
    fetch_impl = fetch_with_timeout(ctx.get("fetchImpl"), ctx.get("timeoutMs"))
    input_from_row = ctx.get("inputFromRow")
    block_private = ctx.get("blockPrivateNetworks", False)
    block_metadata = ctx.get("blockMetadataHosts", True)

    query = _load_query(config)
    variables: dict[str, Any] = dict(config.get("variables") or {})

    if config.get("variablesFile"):
        variables = load_json_file(config["variablesFile"])
    if config.get("inputFile"):
        variables = load_json_file(config["inputFile"])
    if input_from_row:
        variables = {**variables, **input_from_row}

    url = resolve_url(
        config["endpoint"],
        base_url,
        block_private_networks=block_private,
        block_metadata_hosts=block_metadata,
    )
    response = fetch_impl(
        url,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            **auth_headers,
            **(config.get("headers") or {}),
        },
        content=json.dumps({"query": query, "variables": variables}),
    )

    text = response.text
    response_headers = dict(response.headers)

    try:
        parsed = json.loads(text) if text else None
    except json.JSONDecodeError:
        parsed = text

    gql_data = parsed.get("data") if isinstance(parsed, dict) and "data" in parsed else parsed
    data = _get_by_path(gql_data, config.get("dataPath"))

    return {
        "status": response.status_code,
        "data": data,
        "headers": response_headers,
        "raw": text,
    }
