from __future__ import annotations

import os

from snapline.core import auth

from .env import require_env


def create_auth():
    """
    Auth0 / Okta (client credentials) — swap tokenUrl for production.

    Mock demo server:
      tokenUrl: f"{API_BASE_URL}/oauth/token"

    Auth0:
      tokenUrl: https://YOUR_TENANT.auth0.com/oauth/token
      scope: read:graphql write:graphql

    Okta:
      tokenUrl: https://YOUR_DOMAIN.okta.com/oauth2/default/v1/token
      scope: snapline.graphql
    """
    base_url = require_env("API_BASE_URL")
    token_url = os.environ.get("AUTH_TOKEN_URL", f"{base_url}/oauth/token")
    return auth.oauth2(
        {
            "tokenUrl": token_url,
            "clientId": require_env("CLIENT_ID"),
            "clientSecret": require_env("CLIENT_SECRET"),
            "scope": os.environ.get("AUTH_SCOPE", "read:graphql write:graphql"),
        }
    )
