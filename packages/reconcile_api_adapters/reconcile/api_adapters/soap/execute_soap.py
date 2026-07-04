from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

from ..resolve_url import resolve_url
from ..soap.xml_utils import build_soap_envelope, parse_soap_body
from ..types import ApiExecuteContext, ApiExecuteResult, SoapApiConfig


def _default_fetch(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    content: str | bytes | None = None,
    data: str | bytes | None = None,
) -> httpx.Response:
    body = content if content is not None else data
    return httpx.request(method, url, headers=headers, content=body)


def _load_envelope(config: SoapApiConfig) -> str:
    if config.get("envelope"):
        return config["envelope"]

    input_file = config.get("inputFile")
    if input_file:
        return Path(input_file).read_text(encoding="utf-8")

    return build_soap_envelope(
        "<GetUserRequest><email>unknown@example.com</email></GetUserRequest>"
    )


def execute_soap(
    config: SoapApiConfig,
    context: ApiExecuteContext | dict[str, Any] | None = None,
) -> ApiExecuteResult:
    ctx = context or {}
    base_url = ctx.get("baseUrl")
    auth_headers = ctx.get("authHeaders", {})
    fetch_impl = ctx.get("fetchImpl") or _default_fetch
    input_from_row = ctx.get("inputFromRow")

    envelope = _load_envelope(config)

    if input_from_row and input_from_row.get("email"):
        import re

        envelope = re.sub(
            r"<email>[^<]*</email>",
            f"<email>{input_from_row['email']}</email>",
            envelope,
            flags=re.IGNORECASE,
        )

    url = resolve_url(config["endpoint"], base_url)
    headers: dict[str, str] = {
        "Content-Type": "text/xml; charset=utf-8",
        "Accept": "text/xml",
        **auth_headers,
        **(config.get("headers") or {}),
    }

    if config.get("soapAction"):
        headers["SOAPAction"] = config["soapAction"]

    response = fetch_impl(
        url,
        method="POST",
        headers=headers,
        content=envelope,
    )

    text = response.text
    response_headers = dict(response.headers)
    data = parse_soap_body(text)

    return {
        "status": response.status_code,
        "data": data,
        "headers": response_headers,
        "raw": text,
    }
