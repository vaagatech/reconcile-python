from __future__ import annotations

from typing import Any

from .basic_auth_adapter import BasicAuthAdapter
from .oauth2_adapter import OAuth2Adapter
from .openid_adapter import OpenIdAdapter


class AuthFactory:
    @staticmethod
    def basic(config: dict[str, str]) -> BasicAuthAdapter:
        return BasicAuthAdapter(config)

    @staticmethod
    def oauth2(config: dict[str, Any]) -> OAuth2Adapter:
        return OAuth2Adapter(config)

    @staticmethod
    def openid(config: dict[str, Any]) -> OpenIdAdapter:
        return OpenIdAdapter(config)


auth = AuthFactory()
