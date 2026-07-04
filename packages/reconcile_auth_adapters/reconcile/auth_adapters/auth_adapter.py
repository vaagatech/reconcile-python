from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

ConfigT = TypeVar("ConfigT")


class AuthAdapter(ABC, Generic[ConfigT]):
    def __init__(self, config: ConfigT) -> None:
        self.config = config
        self.headers: dict[str, str] = {}
        self.token: str | None = None

    @abstractmethod
    async def initialize(self) -> dict[str, Any]:
        raise NotImplementedError

    def get_headers(self) -> dict[str, str]:
        return dict(self.headers)

    def get_token(self) -> str | None:
        return self.token
