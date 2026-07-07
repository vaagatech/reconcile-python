from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx

DEFAULT_TIMEOUT_MS = 30_000
DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=10.0)

FetchImpl = Callable[..., httpx.Response]


def default_fetch(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    content: str | bytes | None = None,
    data: str | bytes | None = None,
    timeout: httpx.Timeout | None = None,
) -> httpx.Response:
    body = content if content is not None else data
    return httpx.request(
        method,
        url,
        headers=headers,
        content=body,
        timeout=timeout or DEFAULT_TIMEOUT,
    )


def fetch_with_timeout(
    fetch_impl: FetchImpl | None = None,
    timeout_ms: int | None = None,
) -> FetchImpl:
    impl = fetch_impl or default_fetch
    if not timeout_ms:
        return impl

    timeout = httpx.Timeout(timeout_ms / 1000.0, connect=min(10.0, timeout_ms / 1000.0))

    def wrapped(
        url: str,
        *,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        content: str | bytes | None = None,
        data: str | bytes | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        return impl(
            url,
            method=method,
            headers=headers,
            content=content,
            data=data,
            timeout=timeout,
            **kwargs,
        )

    return wrapped
