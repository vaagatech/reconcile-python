from __future__ import annotations

from typing import Any, Literal, Protocol

from snapline.api_adapters.types import ApiRequestConfig
from snapline.auth_adapters import AuthAdapter
from snapline.engine.types import DataMappingMap, DiffResult, ReconcileOptions, TransformationMap

DbRow = dict[str, Any]
DbDialect = Literal["postgres", "mysql", "sqlite"]


class DbConnectionLike(Protocol):
    async def query(self, query: str, params: dict[str, Any] | None = None) -> list[DbRow]: ...


class DbQueryConfig(dict):
    db: DbConnectionLike
    query: str
    params: dict[str, Any] | None


class ApiFileTestConfig(ReconcileOptions):
    endpoint: str | None
    method: str | None
    inputFile: str | None
    expectedFile: str | None
    body: Any
    headers: dict[str, str] | None
    expectedStatus: int | None
    protocol: Literal["rest", "soap", "graphql"] | None
    soapAction: str | None
    envelope: str | None
    query: str | None
    queryFile: str | None
    variables: dict[str, Any] | None
    variablesFile: str | None
    dataPath: str | None


class DbComparisonConfig(ReconcileOptions):
    sourceDb: DbConnectionLike
    targetDb: DbConnectionLike
    query: str | None
    params: dict[str, Any] | None
    sourceQuery: str | None
    targetQuery: str | None
    sourceParams: dict[str, Any] | None
    targetParams: dict[str, Any] | None
    linkKeys: dict[str, str] | None
    sourceCollection: str | None
    targetCollection: str | None
    sourceFilter: dict[str, Any] | None
    targetFilter: dict[str, Any] | None


class ApiToDbConfig(ReconcileOptions):
    api: ApiRequestConfig
    db: DbQueryConfig


class DbToApiConfig(ReconcileOptions):
    db: DbQueryConfig
    api: ApiRequestConfig
    inputFromDb: bool | None


class TestSuiteConfig(dict):
    auth: AuthAdapter | None
    api: ApiFileTestConfig | None
    dbComparison: DbComparisonConfig | None
    apiToDb: ApiToDbConfig | None
    dbToApi: DbToApiConfig | None
    baseUrl: str | None
    fetchImpl: Any | None


class TestStepResult(dict):
    step: str
    passed: bool
    message: str | None
    data: Any
    diff: DiffResult | None
    processed: Any
    token: str | None
    source: Any
    target: Any
    match: bool | None


class TestSuiteResult(dict):
    name: str
    passed: bool
    results: list[TestStepResult]


class CrossSystemResult(dict):
    match: bool
    source: Any
    target: Any
    diff: DiffResult | None


DbComparisonResult = CrossSystemResult
