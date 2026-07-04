from __future__ import annotations

import base64
from typing import Any

from .auth_adapter import AuthAdapter


class BasicAuthAdapter(AuthAdapter[dict[str, str]]):
    async def initialize(self) -> dict[str, Any]:
        username = self.config.get("username")
        password = self.config.get("password")
        if not username or not password:
            raise ValueError("BasicAuthAdapter requires username and password")

        encoded = base64.b64encode(f"{username}:{password}".encode()).decode()
        self.headers = {"Authorization": f"Basic {encoded}"}
        self.token = encoded
        return {"headers": self.get_headers(), "token": self.token}
