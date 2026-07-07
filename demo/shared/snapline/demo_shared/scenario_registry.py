"""Single source of truth for demo scenarios — used by run-all and demo:run."""

from __future__ import annotations

from typing import TypedDict

DOCS_URL = "https://vaagatech.github.io/snapline-python/"
NODE_DOCS_URL = "https://vaagatech.github.io/snapline/"


class ScenarioMeta(TypedDict):
    title: str
    modes: list[str]
    needs_server: bool
    needs_database: bool
    fixtures: list[str]


SCENARIO_ORDER: list[str] = [
    "snapline-ignore-fields",
    "snapline-transformations",
    "snapline-data-mapping-lookup",
    "db-vs-db-sqlite",
    "db-vs-db-cross-dialect",
    "nosql-vs-nosql",
    "snapline-data-mapping-function",
    "db-comparison-transformations",
    "snapline-combined-options",
    "api-vs-file-rest",
    "api-vs-file-rest-cases",
    "api-vs-file-graphql",
    "api-vs-file-soap",
    "api-vs-db-rest",
    "api-vs-db-graphql",
    "api-vs-db-soap",
    "db-vs-api-rest",
    "db-vs-api-graphql",
    "db-vs-api-soap",
    "project-graphql",
    "project-db",
]

SCENARIO_META: dict[str, ScenarioMeta] = {
    "snapline-ignore-fields": {
        "title": "Snapline: ignoreFields (nested paths)",
        "modes": ["api", "api-vs-file"],
        "needs_server": True,
        "needs_database": False,
        "fixtures": ["tracked-expected.json"],
    },
    "snapline-transformations": {
        "title": "Snapline: transformations (offline fixture cases)",
        "modes": ["runSnaplineFixtureCases", "transformations"],
        "needs_server": False,
        "needs_database": False,
        "fixtures": [],
    },
    "snapline-data-mapping-lookup": {
        "title": "Snapline: dataMapping lookup table (offline fixture cases)",
        "modes": ["runSnaplineFixtureCases", "dataMapping"],
        "needs_server": False,
        "needs_database": False,
        "fixtures": [],
    },
    "db-vs-db-sqlite": {
        "title": "DB vs DB (SQLite — same query + linkKeys)",
        "modes": ["dbComparison", "sourceQuery", "linkKeys"],
        "needs_server": False,
        "needs_database": True,
        "fixtures": [],
    },
    "db-vs-db-cross-dialect": {
        "title": "DB vs DB (Postgres vs MySQL seedDb stub)",
        "modes": ["dbComparison", "dataMapping"],
        "needs_server": False,
        "needs_database": False,
        "fixtures": [],
    },
    "nosql-vs-nosql": {
        "title": "NoSQL vs NoSQL (document stores + linkKeys)",
        "modes": ["dbComparison", "nosql"],
        "needs_server": False,
        "needs_database": False,
        "fixtures": [],
    },
    "snapline-data-mapping-function": {
        "title": "Snapline: dataMapping function (fixture cases + DB)",
        "modes": ["runSnaplineFixtureCases", "dataMapping", "dbComparison"],
        "needs_server": False,
        "needs_database": True,
        "fixtures": [],
    },
    "db-comparison-transformations": {
        "title": "Snapline: transformations (DB vs DB)",
        "modes": ["dbComparison", "transformations"],
        "needs_server": False,
        "needs_database": True,
        "fixtures": [],
    },
    "snapline-combined-options": {
        "title": "Snapline: combined options (API vs DB)",
        "modes": ["apiToDb", "ignoreFields", "transformations", "dataMapping"],
        "needs_server": True,
        "needs_database": True,
        "fixtures": [],
    },
    "api-vs-file-rest": {
        "title": "API vs file (REST + OAuth2)",
        "modes": ["api", "api-vs-file", "auth"],
        "needs_server": True,
        "needs_database": False,
        "fixtures": ["rest-input.json", "rest-expected.json"],
    },
    "api-vs-file-rest-cases": {
        "title": "API vs file (REST fixture cases + OAuth2)",
        "modes": ["runApiFixtureCases", "api-vs-file", "auth"],
        "needs_server": True,
        "needs_database": False,
        "fixtures": [],
    },
    "api-vs-file-graphql": {
        "title": "API vs file (GraphQL fixture cases + OAuth2)",
        "modes": ["runApiFixtureCases", "api-vs-file", "auth"],
        "needs_server": True,
        "needs_database": False,
        "fixtures": [],
    },
    "api-vs-file-soap": {
        "title": "API vs file (SOAP)",
        "modes": ["api", "api-vs-file", "soap"],
        "needs_server": True,
        "needs_database": False,
        "fixtures": ["soap-request.xml", "soap-expected.json"],
    },
    "api-vs-db-rest": {
        "title": "API vs DB (REST vs SQLite JOIN)",
        "modes": ["apiToDb"],
        "needs_server": True,
        "needs_database": True,
        "fixtures": [],
    },
    "api-vs-db-graphql": {
        "title": "API vs DB (GraphQL + OAuth2 vs SQLite JOIN)",
        "modes": ["apiToDb", "auth"],
        "needs_server": True,
        "needs_database": True,
        "fixtures": ["graphql-variables.json"],
    },
    "api-vs-db-soap": {
        "title": "API vs DB (SOAP vs SQLite JOIN)",
        "modes": ["apiToDb", "soap"],
        "needs_server": True,
        "needs_database": True,
        "fixtures": ["soap-request.xml"],
    },
    "db-vs-api-rest": {
        "title": "DB vs API (SQLite JOIN vs REST)",
        "modes": ["dbToApi", "inputFromDb"],
        "needs_server": True,
        "needs_database": True,
        "fixtures": [],
    },
    "db-vs-api-graphql": {
        "title": "DB vs API (SQLite JOIN vs OAuth2 GraphQL)",
        "modes": ["dbToApi", "inputFromDb", "auth"],
        "needs_server": True,
        "needs_database": True,
        "fixtures": [],
    },
    "db-vs-api-soap": {
        "title": "DB vs API (SQLite JOIN vs SOAP)",
        "modes": ["dbToApi", "inputFromDb", "soap"],
        "needs_server": True,
        "needs_database": True,
        "fixtures": ["soap-request.xml"],
    },
    "project-graphql": {
        "title": "Project GraphQL — 3 operations (Auth0/Okta fixture cases)",
        "modes": ["runApiFixtureCases", "graphql", "auth"],
        "needs_server": True,
        "needs_database": False,
        "fixtures": [],
    },
    "project-db": {
        "title": "Project DB — SQL warehouse → NoSQL streamed consistency",
        "modes": ["runWarehouseComparison", "dbComparison", "streaming"],
        "needs_server": False,
        "needs_database": False,
        "fixtures": [],
    },
}


def validate_scenario_registry(scenarios_dir) -> None:
    on_disk = sorted(path.name for path in scenarios_dir.iterdir() if path.is_dir())

    for scenario_id in SCENARIO_ORDER:
        if scenario_id not in SCENARIO_META:
            raise ValueError(f"Missing SCENARIO_META for {scenario_id!r}")
        if scenario_id not in on_disk:
            raise ValueError(f"Scenario directory missing on disk: demo/scenarios/{scenario_id}")

    unknown = [scenario_id for scenario_id in on_disk if scenario_id not in SCENARIO_ORDER]
    if unknown:
        raise ValueError(
            "Scenario directories not listed in SCENARIO_ORDER: "
            f"{', '.join(unknown)}. Add them to demo/scripts/scenario_registry.py"
        )
