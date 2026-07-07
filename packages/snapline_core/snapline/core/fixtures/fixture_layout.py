from __future__ import annotations

from pathlib import Path

from .types import FixtureCaseDefaults, FixtureCaseMeta, FixtureLayout, ResolvedFixtureLayout

DEFAULT_FIXTURE_LAYOUT: ResolvedFixtureLayout = {
    "casesDir": "cases",
    "caseMetaFile": "case.json",
    "expectedFile": "expected.json",
    "liveFile": "live.json",
    "queryFile": "query.graphql",
    "variablesFile": "variables.json",
    "restInputFile": "input.json",
    "soapInputFile": "input.xml",
}


def resolve_fixture_layout(
    layout: FixtureLayout | None = None,
    defaults: FixtureCaseDefaults | None = None,
    meta: FixtureCaseMeta | None = None,
) -> ResolvedFixtureLayout:
    return {
        "casesDir": (layout or {}).get("casesDir", DEFAULT_FIXTURE_LAYOUT["casesDir"]),
        "caseMetaFile": (
            (meta or {}).get("caseMetaFile")
            or (defaults or {}).get("caseMetaFile")
            or (layout or {}).get("caseMetaFile")
            or DEFAULT_FIXTURE_LAYOUT["caseMetaFile"]
        ),
        "expectedFile": (
            (meta or {}).get("expectedFile")
            or (defaults or {}).get("expectedFile")
            or (layout or {}).get("expectedFile")
            or DEFAULT_FIXTURE_LAYOUT["expectedFile"]
        ),
        "liveFile": (
            (meta or {}).get("liveFile")
            or (defaults or {}).get("liveFile")
            or (layout or {}).get("liveFile")
            or DEFAULT_FIXTURE_LAYOUT["liveFile"]
        ),
        "queryFile": (
            (meta or {}).get("queryFile")
            or (defaults or {}).get("queryFile")
            or (layout or {}).get("queryFile")
            or DEFAULT_FIXTURE_LAYOUT["queryFile"]
        ),
        "variablesFile": (
            (meta or {}).get("variablesFile")
            or (defaults or {}).get("variablesFile")
            or (layout or {}).get("variablesFile")
            or DEFAULT_FIXTURE_LAYOUT["variablesFile"]
        ),
        "restInputFile": (
            (meta or {}).get("restInputFile")
            or (defaults or {}).get("restInputFile")
            or (layout or {}).get("restInputFile")
            or DEFAULT_FIXTURE_LAYOUT["restInputFile"]
        ),
        "soapInputFile": (
            (meta or {}).get("soapInputFile")
            or (defaults or {}).get("soapInputFile")
            or (layout or {}).get("soapInputFile")
            or DEFAULT_FIXTURE_LAYOUT["soapInputFile"]
        ),
    }


def case_file_path(case_dir: str | Path, file_name: str) -> str:
    return str(Path(case_dir) / file_name)
