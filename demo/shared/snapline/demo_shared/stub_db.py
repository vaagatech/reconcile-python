from __future__ import annotations

import re
from typing import Any

from snapline.core.types import DbDialect, DbRow

from .sqlite_connection import SqliteConnection, create_sqlite_connection


class DbConnection:
    """Demo-only in-memory DB stub — not part of snapline-core."""

    def __init__(
        self,
        dialect: DbDialect,
        connection_string: str,
        rows: list[DbRow] | None = None,
    ) -> None:
        self.dialect = dialect
        self.connection_string = connection_string
        self._rows = list(rows or [])

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


_db_registry: dict[str, list[DbRow]] = {}


def seed_db(connection_string: str, rows: list[DbRow]) -> None:
    _db_registry[connection_string] = rows


def clear_db_seeds(connection_string: str | None = None) -> None:
    if connection_string is None:
        _db_registry.clear()
        return
    _db_registry.pop(connection_string, None)


def create_db_connection(dialect: DbDialect, connection_string: str) -> DbConnection:
    seed = _db_registry.get(connection_string, [])
    return DbConnection(dialect, connection_string, seed)


class DbFactory:
    @staticmethod
    def postgres(connection_string: str) -> DbConnection:
        return create_db_connection("postgres", connection_string)

    @staticmethod
    def mysql(connection_string: str) -> DbConnection:
        return create_db_connection("mysql", connection_string)

    @staticmethod
    def sqlite(path: str = ":memory:") -> SqliteConnection:
        return create_sqlite_connection(path)

    @staticmethod
    def seed(connection_string: str, rows: list[DbRow]) -> None:
        seed_db(connection_string, rows)


db = DbFactory()
