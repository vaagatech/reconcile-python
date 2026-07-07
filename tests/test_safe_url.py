from __future__ import annotations

import pytest
from snapline.api_adapters.resolve_url import resolve_url
from snapline.api_adapters.safe_url import assert_safe_url


def test_assert_safe_url_blocks_metadata_host():
    with pytest.raises(ValueError, match="Blocked metadata host"):
        assert_safe_url("http://169.254.169.254/latest/meta-data/")


def test_assert_safe_url_allows_public_host():
    assert_safe_url("https://api.example.com/users")


def test_resolve_url_blocks_metadata_when_joined_with_base():
    with pytest.raises(ValueError, match="Blocked metadata host"):
        resolve_url(
            "http://169.254.169.254/",
            "https://api.example.com",
            block_metadata_hosts=True,
        )


def test_resolve_url_blocks_private_network_when_enabled():
    with pytest.raises(ValueError, match="Blocked private-network host"):
        resolve_url(
            "http://127.0.0.1/health",
            block_private_networks=True,
            block_metadata_hosts=False,
        )
