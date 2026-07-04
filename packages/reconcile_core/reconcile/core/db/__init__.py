from __future__ import annotations

from typing import Any

from ..types import DbRow
from .db_connection import DbConnection
from .sqlite_connection import (
    SqliteConnection,
    create_sqlite_connection,
    exec_sqlite_file,
    exec_sqlite_sql,
)

_db_registry: dict[str, list[DbRow]] = {}


def seed_db(connection_string: str, rows: list[DbRow]) -> None:
    _db_registry[connection_string] = rows


def create_db_connection(dialect: str, connection_string: str) -> DbConnection:
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

__all__ = [
    "SqliteConnection",
    "create_sqlite_connection",
    "db",
    "exec_sqlite_file",
    "exec_sqlite_sql",
    "seed_db",
]
