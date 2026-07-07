from __future__ import annotations

from urllib.parse import urljoin, urlparse

from .safe_url import assert_safe_url


def resolve_url(
    endpoint: str,
    base_url: str | None = None,
    *,
    block_private_networks: bool = False,
    block_metadata_hosts: bool = True,
) -> str:
    if urlparse(endpoint).scheme:
        resolved = endpoint
    elif not base_url:
        resolved = endpoint
    else:
        resolved = urljoin(base_url.rstrip("/") + "/", endpoint.lstrip("/"))

    assert_safe_url(
        resolved,
        block_private_networks=block_private_networks,
        block_metadata_hosts=block_metadata_hosts,
    )
    return resolved
