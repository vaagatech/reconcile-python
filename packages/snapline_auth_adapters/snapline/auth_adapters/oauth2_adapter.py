from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

import httpx

from .auth_adapter import AuthAdapter


def _default_fetch(url: str, *, method: str = "GET", headers=None, content=None, data=None):
    body = content if content is not None else data
    return httpx.request(method, url, headers=headers, content=body)


class OAuth2Adapter(AuthAdapter[dict[str, Any]]):
    async def initialize(self) -> dict[str, Any]:
        token_url = self.config.get("tokenUrl")
        client_id = self.config.get("clientId")
        client_secret = self.config.get("clientSecret")
        scope = self.config.get("scope")
        fetch_impl = self.config.get("fetchImpl") or _default_fetch

        if not token_url or not client_id or not client_secret:
            raise ValueError("OAuth2Adapter requires tokenUrl, clientId, and clientSecret")

        body = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
        if scope:
            body["scope"] = scope

        response = fetch_impl(
            token_url,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            content=urlencode(body),
        )

        if response.status_code >= 400:
            raise RuntimeError(
                f"OAuth2 token request failed ({response.status_code}): {response.text}"
            )

        payload = response.json()
        self.token = payload.get("access_token")
        if not self.token:
            raise RuntimeError("OAuth2 response did not include access_token")

        self.headers = {"Authorization": f"Bearer {self.token}"}
        if payload.get("token_type"):
            self.headers["X-Token-Type"] = payload["token_type"]

        return {"headers": self.get_headers(), "token": self.token}
