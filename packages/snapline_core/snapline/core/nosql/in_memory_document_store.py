from __future__ import annotations

from typing import Any

from .types import DbRow


class InMemoryDocumentStore:
    def __init__(self) -> None:
        self._collections: dict[str, list[DbRow]] = {}

    def seed(self, collection: str, documents: list[DbRow]) -> None:
        self._collections[collection] = [dict(doc) for doc in documents]

    async def find(self, collection: str, filter: dict[str, Any] | None = None) -> list[DbRow]:
        docs = self._collections.get(collection, [])
        filter_entries = list((filter or {}).items())

        if not filter_entries:
            return [dict(doc) for doc in docs]

        return [
            dict(doc)
            for doc in docs
            if all(doc.get(key) == value for key, value in filter_entries)
        ]

    async def find_one(self, collection: str, filter: dict[str, Any] | None = None) -> DbRow | None:
        rows = await self.find(collection, filter)
        return rows[0] if rows else None
