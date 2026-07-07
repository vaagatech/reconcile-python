from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any

from snapline.core.types import DbRow


def _normalize_named_params(query: str) -> str:
    return re.sub(r":([a-zA-Z_][a-zA-Z0-9_]*)", r"@\1", query)


class SqliteConnection:
    """Demo-only SQLite adapter — not part of snapline-core."""

    def __init__(self, database: sqlite3.Connection) -> None:
        self._database = database

    def exec(self, sql: str) -> None:
        self._database.executescript(sql)

    async def query(self, query: str, params: dict[str, Any] | None = None) -> list[DbRow]:
        normalized = _normalize_named_params(query)
        cursor = self._database.execute(normalized, params or {})
        columns = [description[0] for description in cursor.description or []]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def close(self) -> None:
        self._database.close()


def create_sqlite_connection(path: str = ":memory:") -> SqliteConnection:
    database = sqlite3.connect(path)
    database.row_factory = sqlite3.Row
    database.execute("PRAGMA foreign_keys = ON")
    return SqliteConnection(database)


def exec_sqlite_sql(connection: SqliteConnection, sql: str) -> None:
    connection.exec(sql)


def exec_sqlite_file(connection: SqliteConnection, file_path: str | Path) -> None:
    connection.exec(Path(file_path).read_text(encoding="utf-8"))
