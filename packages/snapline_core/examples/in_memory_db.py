from __future__ import annotations

import re
from typing import Any

from snapline.core.types import DbRow


class InMemoryDb:
    """Minimal DbConnectionLike for package examples — not shipped as a driver."""

    def __init__(self, rows: list[DbRow]) -> None:
        self._rows = list(rows)

    async def query(self, query: str, params: dict[str, Any] | None = None) -> list[DbRow]:
        normalized = re.sub(r"\s+", " ", query).strip().lower()
        if not normalized.startswith("select"):
            raise ValueError(f"Unsupported query: {query}")

        results = list(self._rows)
        params = params or {}

        for key, value in params.items():
            results = [row for row in results if row.get(key) == value]

        columns_match = re.search(r"select\s+(.+?)\s+from", query, flags=re.IGNORECASE)
        if columns_match and columns_match.group(1).strip() != "*":
            columns = [column.strip() for column in columns_match.group(1).split(",")]
            projected: list[DbRow] = []
            for row in results:
                projected.append({column: row[column] for column in columns if column in row})
            results = projected

        return results
