from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl

from snapline.engine import load_json_file

from ..http_client import default_fetch, fetch_with_timeout
from ..resolve_url import resolve_url
from ..types import ApiExecuteContext, ApiExecuteResult, RestApiConfig


def execute_rest(
    config: RestApiConfig,
    context: ApiExecuteContext | dict[str, Any] | None = None,
) -> ApiExecuteResult:
    ctx = context or {}
    base_url = ctx.get("baseUrl")
    auth_headers = ctx.get("authHeaders", {})
    fetch_impl = fetch_with_timeout(ctx.get("fetchImpl"), ctx.get("timeoutMs"))
    input_from_row = ctx.get("inputFromRow")
    block_private = ctx.get("blockPrivateNetworks", False)
    block_metadata = ctx.get("blockMetadataHosts", True)

    endpoint = config["endpoint"]
    method = config.get("method") or "GET"
    input_file = config.get("inputFile")
    body = config.get("body")
    headers = config.get("headers") or {}

    url = resolve_url(
        endpoint,
        base_url,
        block_private_networks=block_private,
        block_metadata_hosts=block_metadata,
    )
    payload: Any = body

    if input_file:
        payload = load_json_file(input_file)

    if input_from_row:
        if isinstance(payload, dict) and not isinstance(payload, list):
            payload = {**payload, **input_from_row}
        else:
            payload = dict(input_from_row)

    http_method = method.upper()
    if input_from_row and http_method in {"GET", "HEAD"}:
        parsed = urlparse(url)
        query = dict(parse_qsl(parsed.query))
        query.update({key: str(value) for key, value in input_from_row.items()})
        url = urlunparse(parsed._replace(query=urlencode(query)))

    request_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        **auth_headers,
        **headers,
    }

    request_body: str | None = None
    if payload is not None and http_method not in {"GET", "HEAD"}:
        request_body = json.dumps(payload)

    response = fetch_impl(
        url,
        method=http_method,
        headers=request_headers,
        content=request_body,
    )

    text = response.text
    response_headers = dict(response.headers)

    try:
        data = json.loads(text) if text else None
    except json.JSONDecodeError:
        data = text

    return {
        "status": response.status_code,
        "data": data,
        "headers": response_headers,
        "raw": text,
    }
