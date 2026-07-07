from __future__ import annotations

from snapline.core import auth

from .env import require_env


def create_auth():
    base_url = require_env("API_BASE_URL")
    return auth.oauth2(
        {
            "tokenUrl": f"{base_url}/oauth/token",
            "clientId": require_env("CLIENT_ID"),
            "clientSecret": require_env("CLIENT_SECRET"),
        }
    )
