from __future__ import annotations

from typing import Any, Protocol

DbRow = dict[str, Any]


class DocumentStoreLike(Protocol):
    async def find(self, collection: str, filter: dict[str, Any] | None = None) -> list[DbRow]: ...

    async def find_one(self, collection: str, filter: dict[str, Any] | None = None) -> DbRow | None: ...
