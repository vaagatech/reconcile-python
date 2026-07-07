from __future__ import annotations

from typing import Any, Literal, TypedDict

from snapline.engine.types import SnaplineOptions

FixturePresetRef = str


class FixtureFileNames(TypedDict, total=False):
    caseMetaFile: str
    expectedFile: str
    liveFile: str
    queryFile: str
    variablesFile: str
    restInputFile: str
    soapInputFile: str


class FixtureCaseMeta(TypedDict, total=False):
    name: str
    expectMatch: bool
    failureType: Literal["dataMapping", "transformation", "auth"]
    expectedDiffPath: str
    skipAuth: bool
    expectStatus: int
    dataPath: str
    endpoint: str
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"]
    protocol: Literal["rest", "graphql", "soap"]
    soapAction: str
    ignoreFields: list[str]
    transformations: SnaplineOptions["transformations"] | FixturePresetRef
    dataMapping: SnaplineOptions["dataMapping"] | FixturePresetRef
    caseMetaFile: str
    expectedFile: str
    liveFile: str
    queryFile: str
    variablesFile: str
    restInputFile: str
    soapInputFile: str


class FixtureCaseDefaults(TypedDict, total=False):
    ignoreFields: list[str]
    transformations: SnaplineOptions["transformations"] | FixturePresetRef
    dataMapping: SnaplineOptions["dataMapping"] | FixturePresetRef
    caseMetaFile: str
    expectedFile: str
    liveFile: str
    queryFile: str
    variablesFile: str
    restInputFile: str
    soapInputFile: str
    endpoint: str
    protocol: Literal["rest", "graphql", "soap"]
    dataPath: str


class FixtureCasePresetMaps(TypedDict, total=False):
    transformations: dict[str, SnaplineOptions["transformations"]]
    dataMapping: dict[str, SnaplineOptions["dataMapping"]]


class FixtureLayout(TypedDict, total=False):
    casesDir: str
    caseMetaFile: str
    expectedFile: str
    liveFile: str
    queryFile: str
    variablesFile: str
    restInputFile: str
    soapInputFile: str


class ResolvedFixtureLayout(TypedDict):
    casesDir: str
    caseMetaFile: str
    expectedFile: str
    liveFile: str
    queryFile: str
    variablesFile: str
    restInputFile: str
    soapInputFile: str


class RunApiFixtureCasesOptions(TypedDict, total=False):
    suiteName: str
    fixturesRoot: str
    baseUrl: str
    auth: Any
    authHeaders: dict[str, str]
    layout: FixtureLayout
    defaults: FixtureCaseDefaults
    presets: FixtureCasePresetMaps
    caseIds: list[str]
    fetchImpl: Any
    timeoutMs: int
    blockPrivateNetworks: bool
    blockMetadataHosts: bool


class RunSnaplineFixtureCasesOptions(TypedDict, total=False):
    suiteName: str
    fixturesRoot: str
    layout: FixtureLayout
    defaults: FixtureCaseDefaults
    presets: FixtureCasePresetMaps
    caseIds: list[str]
