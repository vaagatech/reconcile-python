from __future__ import annotations

from typing import Protocol

from .sqlite_setup import DemoDatabase


class ScenarioContext:
    def __init__(self, base_url: str, database: DemoDatabase | None = None) -> None:
        self.base_url = base_url
        self.database = database


class ScenarioModule(Protocol):
    name: str
    needs_server: bool
    needs_database: bool

    async def run(self, context: ScenarioContext) -> dict: ...
