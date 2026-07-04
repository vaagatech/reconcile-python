from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from ..types import TestSuiteResult

ReportFormat = Literal["json", "html", "text"]


class ReportConfig(dict):
    format: ReportFormat
    outputPath: str


class TestRunReportMeta(dict):
    durationMs: int | None
    environment: dict[str, Any] | None


class TestRunReport(dict):
    generatedAt: str
    framework: str
    summary: dict[str, Any]
    environment: dict[str, Any] | None
    suites: list[TestSuiteResult]
