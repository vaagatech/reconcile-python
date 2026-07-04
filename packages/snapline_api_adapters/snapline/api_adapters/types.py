from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal, Protocol, TypeAlias

HttpMethod: TypeAlias = Literal["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"]
ApiProtocol: TypeAlias = Literal["rest", "soap", "graphql"]


class FetchResponse(Protocol):
    status_code: int
    text: str
    headers: dict[str, str]

    def json(self) -> Any: ...


class FetchImpl(Protocol):
    def __call__(
        self,
        url: str,
        *,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        content: str | bytes | None = None,
        data: str | bytes | None = None,
    ) -> FetchResponse: ...


class ApiExecuteContext(dict):
    baseUrl: str | None
    authHeaders: dict[str, str]
    fetchImpl: FetchImpl | None
    inputFromRow: dict[str, Any] | None


class ApiExecuteResult(dict):
    status: int
    data: Any
    headers: dict[str, str]
    raw: str


class RestApiConfig(dict):
    protocol: Literal["rest"]
    endpoint: str
    method: HttpMethod | None
    inputFile: str | None
    body: Any
    headers: dict[str, str] | None


class SoapApiConfig(dict):
    protocol: Literal["soap"]
    endpoint: str
    soapAction: str | None
    envelope: str | None
    inputFile: str | None
    headers: dict[str, str] | None


class GraphqlApiConfig(dict):
    protocol: Literal["graphql"]
    endpoint: str
    query: str | None
    queryFile: str | None
    variables: dict[str, Any] | None
    variablesFile: str | None
    inputFile: str | None
    dataPath: str | None
    headers: dict[str, str] | None


ApiRequestConfig = RestApiConfig | SoapApiConfig | GraphqlApiConfig


def is_rest_config(config: ApiRequestConfig) -> bool:
    return config.get("protocol") == "rest"


def is_soap_config(config: ApiRequestConfig) -> bool:
    return config.get("protocol") == "soap"


def is_graphql_config(config: ApiRequestConfig) -> bool:
    return config.get("protocol") == "graphql"
