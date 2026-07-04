from __future__ import annotations

from typing import Any

from .graphql.execute_graphql import execute_graphql
from .rest.execute_rest import execute_rest
from .soap.execute_soap import execute_soap
from .types import (
    ApiExecuteContext,
    ApiExecuteResult,
    ApiRequestConfig,
    is_graphql_config,
    is_rest_config,
    is_soap_config,
)


def execute_api(
    config: ApiRequestConfig,
    context: ApiExecuteContext | dict[str, Any] | None = None,
) -> ApiExecuteResult:
    if is_rest_config(config):
        return execute_rest(config, context)
    if is_soap_config(config):
        return execute_soap(config, context)
    if is_graphql_config(config):
        return execute_graphql(config, context)
    raise ValueError("Unsupported API protocol")
