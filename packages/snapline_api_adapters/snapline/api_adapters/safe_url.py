from __future__ import annotations

import ipaddress
from urllib.parse import urlparse

BLOCKED_HOSTS = {"169.254.169.254", "metadata.google.internal"}


def assert_safe_url(
    url: str,
    *,
    block_private_networks: bool = False,
    block_metadata_hosts: bool = True,
) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"Unsupported URL protocol: {parsed.scheme or '(none)'}")

    host = (parsed.hostname or "").lower()
    if block_metadata_hosts and host in BLOCKED_HOSTS:
        raise ValueError(f"Blocked metadata host: {host}")

    if block_private_networks and host:
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            return
        if address.is_private or address.is_loopback or address.is_link_local:
            raise ValueError(f"Blocked private-network host: {host}")
