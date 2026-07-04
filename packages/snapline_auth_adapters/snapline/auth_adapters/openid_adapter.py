from __future__ import annotations

import base64
import json
from typing import Any

import httpx

from .auth_adapter import AuthAdapter


def _default_fetch(url: str, *, method: str = "GET", headers=None, content=None, data=None):
    body = content if content is not None else data
    return httpx.request(method, url, headers=headers, content=body)


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


class OpenIdAdapter(AuthAdapter[dict[str, Any]]):
    async def initialize(self) -> dict[str, Any]:
        token = self.config.get("token")
        id_token = self.config.get("idToken")
        assertion = self.config.get("assertion")
        fetch_impl = self.config.get("fetchImpl") or _default_fetch

        if token:
            self.token = token
            self.headers = {
                "Authorization": f"Bearer {token}",
                "X-Auth-Protocol": "OpenID",
            }
            return {"headers": self.get_headers(), "token": self.token}

        if id_token:
            self.token = id_token
            self.headers = {
                "Authorization": f"Bearer {id_token}",
                "X-OpenID-Token": id_token,
                "X-Auth-Protocol": "OpenID",
            }
            return {"headers": self.get_headers(), "token": self.token}

        if assertion:
            issuer = assertion.get("issuer")
            subject = assertion.get("subject")
            audience = assertion.get("audience")
            private_key = assertion.get("privateKey")
            token_url = assertion.get("tokenUrl")

            if token_url and fetch_impl:
                response = fetch_impl(
                    token_url,
                    method="POST",
                    headers={"Content-Type": "application/json"},
                    content=json.dumps(
                        {
                            "issuer": issuer,
                            "subject": subject,
                            "audience": audience,
                            "assertion": private_key,
                        }
                    ),
                )

                if response.status_code >= 400:
                    raise RuntimeError(
                        f"OpenID assertion exchange failed ({response.status_code}): {response.text}"
                    )

                payload = response.json()
                self.token = payload.get("access_token") or payload.get("id_token")
            else:
                self.token = _base64url_encode(
                    json.dumps({"iss": issuer, "sub": subject, "aud": audience}).encode()
                )

            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "X-OpenID-Assertion": "true",
                "X-Auth-Protocol": "OpenID",
            }
            return {"headers": self.get_headers(), "token": self.token}

        raise ValueError("OpenIdAdapter requires token, idToken, or assertion config")
