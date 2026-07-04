from __future__ import annotations

from urllib.parse import urljoin, urlparse


def resolve_url(endpoint: str, base_url: str | None = None) -> str:
    if urlparse(endpoint).scheme:
        return endpoint
    if not base_url:
        return endpoint
    return urljoin(base_url.rstrip("/") + "/", endpoint.lstrip("/"))
