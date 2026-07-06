from __future__ import annotations

from typing import Any

from ..nosql.types import DocumentStoreLike
from ..types import DbComparisonConfig, DbConnectionLike, DbRow
from .resolve_link_params import resolve_target_filter_from_source, resolve_target_params_from_source


def is_document_store(store: DbConnectionLike | DocumentStoreLike) -> bool:
    return callable(getattr(store, "find", None))


def _assert_sql_query(query: str | None, label: str) -> str:
    if not query:
        raise ValueError(f"dbComparison requires {label} when using SQL databases")
    return query


def _assert_collection(collection: str | None, label: str) -> str:
    if not collection:
        raise ValueError(f"dbComparison requires {label} when using document stores")
    return collection


async def fetch_source_row(config: DbComparisonConfig | dict[str, Any]) -> DbRow | None:
    source_db = config["sourceDb"]
    params = config.get("params") or {}
    source_params = config.get("sourceParams")
    source_filter = config.get("sourceFilter") or {}

    if is_document_store(source_db):
        collection = _assert_collection(config.get("sourceCollection"), "sourceCollection")
        rows = await source_db.find(collection, source_filter)
        return rows[0] if rows else None

    sql = _assert_sql_query(config.get("sourceQuery") or config.get("query"), "sourceQuery or query")
    rows = await source_db.query(sql, source_params or params)
    return rows[0] if rows else None


async def fetch_target_row(
    config: DbComparisonConfig | dict[str, Any],
    source_row: DbRow | None,
) -> DbRow | None:
    target_db = config["targetDb"]
    params = config.get("params") or {}
    source_params = config.get("sourceParams")
    target_params = config.get("targetParams")
    link_keys = config.get("linkKeys")

    if is_document_store(target_db):
        collection = _assert_collection(config.get("targetCollection"), "targetCollection")
        if source_row is not None:
            filter_value = resolve_target_filter_from_source(
                source_row,
                target_filter=config.get("targetFilter"),
                link_keys=link_keys,
                target_filter_from_source=config.get("targetFilterFromSource"),
                fallback_filter=config.get("sourceFilter"),
            )
        else:
            filter_value = config.get("targetFilter") or config.get("sourceFilter") or {}
        rows = await target_db.find(collection, filter_value)
        return rows[0] if rows else None

    sql = _assert_sql_query(
        config.get("targetQuery") or config.get("query") or config.get("sourceQuery"),
        "targetQuery, query, or sourceQuery",
    )
    resolved_params = (
        resolve_target_params_from_source(
            source_row,
            target_params=target_params,
            link_keys=link_keys,
            target_params_from_source=config.get("targetParamsFromSource"),
            fallback_params=params,
        )
        if source_row is not None
        else (target_params or source_params or params)
    )
    rows = await target_db.query(sql, resolved_params)
    return rows[0] if rows else None
