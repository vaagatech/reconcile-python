from __future__ import annotations

from typing import Any, Callable

DbRow = dict[str, Any]


def resolve_target_params_from_source(
    source_row: DbRow,
    *,
    target_params: dict[str, Any] | None = None,
    link_keys: dict[str, str] | None = None,
    target_params_from_source: Callable[[DbRow], dict[str, Any]] | None = None,
    fallback_params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if target_params_from_source is not None:
        return target_params_from_source(source_row)

    if target_params is not None:
        return target_params

    if link_keys:
        return {param_name: source_row[source_field] for param_name, source_field in link_keys.items()}

    return fallback_params or {}


def resolve_target_filter_from_source(
    source_row: DbRow,
    *,
    target_filter: dict[str, Any] | None = None,
    link_keys: dict[str, str] | None = None,
    target_filter_from_source: Callable[[DbRow], dict[str, Any]] | None = None,
    fallback_filter: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if target_filter_from_source is not None:
        return target_filter_from_source(source_row)

    if target_filter is not None:
        return target_filter

    if link_keys:
        return {filter_field: source_row[source_field] for filter_field, source_field in link_keys.items()}

    return fallback_filter or {}
