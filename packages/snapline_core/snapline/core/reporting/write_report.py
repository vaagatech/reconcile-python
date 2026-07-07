from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..types import TestSuiteResult
from .html_reporter import render_html_report
from .json_reporter import render_json_report
from .redact_fields import redact_suite_results
from .text_reporter import render_text_report
from .types import ReportConfig, TestRunReport, TestRunReportMeta

FRAMEWORK_NAME = "snapline-engine"


def build_report(
    suites: list[TestSuiteResult],
    meta: TestRunReportMeta | dict[str, Any] | None = None,
) -> TestRunReport:
    meta = meta or {}
    passed = sum(1 for suite in suites if suite["passed"])
    failed = len(suites) - passed

    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "framework": FRAMEWORK_NAME,
        "summary": {
            "total": len(suites),
            "passed": passed,
            "failed": failed,
            "durationMs": meta.get("durationMs"),
        },
        "environment": meta.get("environment"),
        "suites": suites,
    }


def render_report(report: TestRunReport, format: str) -> str:
    if format == "json":
        return render_json_report(report)
    if format == "html":
        return render_html_report(report)
    if format == "text":
        return render_text_report(report)
    raise ValueError(f"Unsupported report format: {format}")


def write_test_report(
    suites: list[TestSuiteResult],
    config: ReportConfig | dict[str, Any],
    meta: TestRunReportMeta | dict[str, Any] | None = None,
) -> str:
    sanitized = redact_suite_results(suites, config.get("redactFields"))
    report = build_report(sanitized, meta)
    content = render_report(report, config["format"])
    output_path = Path(config["outputPath"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return str(output_path)
