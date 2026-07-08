from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from snapline.engine import load_json_file

from ..types import DbRow
from .wait_for_result import wait_for_result


def create_db_async_result_resolver(config: dict[str, Any]):
    correlation_param = config.get("correlationParam", "correlationId")
    db = config["db"]
    query = config["query"]
    params = config.get("params") or {}
    until: Callable[[list[DbRow]], bool] | None = config.get("until")
    extract: Callable[[list[DbRow]], Any] | None = config.get("extract")

    class _Resolver:
        async def wait_for_result(self, correlation_id: str, options: dict[str, Any] | None = None) -> Any:
            opts = options or {}

            async def check() -> Any | None:
                rows = await db.query(query, {**params, correlation_param: correlation_id})
                if until is not None and not until(rows):
                    return None
                if extract is not None:
                    return extract(rows)
                return rows[0] if rows else None

            return await wait_for_result(
                check,
                timeout_ms=opts.get("timeoutMs", 30_000),
                interval_ms=opts.get("intervalMs", 250),
            )

    return _Resolver()


def create_file_async_result_resolver(config: dict[str, Any]):
    directory = config["directory"]
    file_name_for: Callable[[str], str] = config.get("fileName") or (lambda cid: f"{cid}.json")
    root = Path(directory)

    class _Resolver:
        async def wait_for_result(self, correlation_id: str, options: dict[str, Any] | None = None) -> Any:
            opts = options or {}
            relative = file_name_for(correlation_id)

            async def check() -> Any | None:
                absolute = root / relative
                if not absolute.exists():
                    return None
                return load_json_file(str(absolute), root_dir=str(root))

            return await wait_for_result(
                check,
                timeout_ms=opts.get("timeoutMs", 30_000),
                interval_ms=opts.get("intervalMs", 250),
            )

    return _Resolver()


def create_message_async_result_resolver(config: dict[str, Any]):
    consumer = config["consumer"]
    topic = config["topic"]
    timeout_ms = config.get("timeoutMs")
    extract = config.get("extract")

    class _Resolver:
        async def wait_for_result(self, correlation_id: str, options: dict[str, Any] | None = None) -> Any:
            opts = options or {}
            message = await consumer.wait_for_message(
                topic,
                {
                    "correlationId": correlation_id,
                    "timeoutMs": opts.get("timeoutMs", timeout_ms or 30_000),
                },
            )
            return extract(message) if extract else message.get("payload")

    return _Resolver()
