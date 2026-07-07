from snapline.api_adapters import api, execute_api, resolve_url
from snapline.auth_adapters import AuthAdapter, auth
from snapline.engine import assert_against_file, load_json_file, reconcile, snapline
from snapline.engine.types import ReconcileOptions, SnaplineOptions, SnaplineResult

from .api_config.to_api_request_config import to_api_request_config
from .cross_system.run_api_to_db import run_api_to_db
from .cross_system.run_db_to_api import run_db_to_api
from .db_comparison.run_db_comparison import run_db_comparison
from .db_comparison.run_warehouse_comparison import run_warehouse_comparison
from .fixtures import (
    DEFAULT_FIXTURE_LAYOUT,
    FixtureCaseDefaults,
    FixtureCaseMeta,
    FixtureCasePresetMaps,
    FixtureFileNames,
    FixtureLayout,
    ResolvedFixtureLayout,
    RunApiFixtureCasesOptions,
    RunSnaplineFixtureCasesOptions,
    run_api_fixture_cases,
    run_snapline_fixture_cases,
)
from .io.module_dir import fixtures_dir, module_dir
from .nosql import InMemoryDocumentStore, nosql
from .reporting.redact_fields import redact_fields, redact_suite_results
from .reporting.resolve_report_config import resolve_report_config
from .reporting.types import ReportConfig, ReportFormat, TestRunReport, TestRunReportMeta
from .reporting.write_report import build_report, render_report, write_test_report
from .reporting.stream_report import create_stream_report_writer, StreamReportWriter
from .test_suite import test_suite
from .types import DbConnectionLike, DbDialect, DbRow

execute_api_request = execute_api

__all__ = [
    "AuthAdapter",
    "DbConnectionLike",
    "DbDialect",
    "DbRow",
    "DEFAULT_FIXTURE_LAYOUT",
    "FixtureCaseDefaults",
    "FixtureCaseMeta",
    "FixtureCasePresetMaps",
    "FixtureFileNames",
    "FixtureLayout",
    "ReportConfig",
    "ReportFormat",
    "ResolvedFixtureLayout",
    "RunApiFixtureCasesOptions",
    "RunSnaplineFixtureCasesOptions",
    "TestRunReport",
    "TestRunReportMeta",
    "api",
    "assert_against_file",
    "auth",
    "build_report",
    "execute_api",
    "execute_api_request",
    "fixtures_dir",
    "InMemoryDocumentStore",
    "load_json_file",
    "module_dir",
    "nosql",
    "reconcile",
    "redact_fields",
    "redact_suite_results",
    "render_report",
    "resolve_report_config",
    "resolve_url",
    "ReconcileOptions",
    "run_api_fixture_cases",
    "run_api_to_db",
    "run_db_comparison",
    "run_warehouse_comparison",
    "run_db_to_api",
    "run_snapline_fixture_cases",
    "snapline",
    "SnaplineOptions",
    "SnaplineResult",
    "test_suite",
    "to_api_request_config",
    "create_stream_report_writer",
    "StreamReportWriter",
    "write_test_report",
]
