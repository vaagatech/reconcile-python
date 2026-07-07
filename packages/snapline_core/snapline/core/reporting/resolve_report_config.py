from __future__ import annotations

import os
import sys
from collections.abc import Callable
from typing import Any

from .types import ReportFormat

VALID_FORMATS: set[ReportFormat] = {"json", "html", "text"}


class ResolveReportConfigOptions(dict):
    argv: list[str] | None
    defaultOutputPath: str | Callable[[ReportFormat], str] | None


def _parse_format(value: str | None) -> ReportFormat | None:
    if not value:
        return None
    normalized = value.lower()
    return normalized if normalized in VALID_FORMATS else None


def _built_in_default_output_path(format: ReportFormat) -> str:
    extension = "txt" if format == "text" else format
    return f"./reports/test-report.{extension}"


def _resolve_default_output_path(
    format: ReportFormat,
    custom: str | Callable[[ReportFormat], str] | None = None,
) -> str:
    if callable(custom):
        return custom(format)
    if custom:
        return custom
    return _built_in_default_output_path(format)


def resolve_report_config(
    argv_or_options: list[str] | ResolveReportConfigOptions | None = None,
) -> dict[str, Any] | None:
    if argv_or_options is None:
        options: dict[str, Any] = {"argv": sys.argv}
    elif isinstance(argv_or_options, list):
        options = {"argv": argv_or_options}
    else:
        options = dict(argv_or_options)

    argv = options.get("argv", sys.argv)
    env_format = _parse_format(os.environ.get("REPORT_FORMAT"))
    env_output = os.environ.get("REPORT_OUTPUT")

    cli_format: ReportFormat | None = None
    cli_output: str | None = None
    cli_redact_fields: list[str] | None = None

    index = 0
    while index < len(argv):
        arg = argv[index]
        if not arg:
            index += 1
            continue
        if arg.startswith("--report-format="):
            cli_format = _parse_format(arg.split("=", 1)[1])
        elif arg == "--report-format":
            cli_format = _parse_format(argv[index + 1] if index + 1 < len(argv) else None)
        elif arg.startswith("--report-output="):
            cli_output = arg.split("=", 1)[1]
        elif arg == "--report-output":
            cli_output = argv[index + 1] if index + 1 < len(argv) else None
        elif arg.startswith("--report-redact-fields="):
            cli_redact_fields = [
                field.strip() for field in arg.split("=", 1)[1].split(",") if field.strip()
            ]
        elif arg == "--report-redact-fields":
            next_arg = argv[index + 1] if index + 1 < len(argv) else ""
            cli_redact_fields = [field.strip() for field in next_arg.split(",") if field.strip()]
        index += 1

    env_redact_fields = [
        field.strip()
        for field in os.environ.get("REPORT_REDACT_FIELDS", "").split(",")
        if field.strip()
    ]

    report_format = cli_format or env_format
    if not report_format:
        return None

    config: dict[str, Any] = {
        "format": report_format,
        "outputPath": cli_output
        or env_output
        or _resolve_default_output_path(report_format, options.get("defaultOutputPath")),
    }

    redact_fields = cli_redact_fields or env_redact_fields or None
    if redact_fields:
        config["redactFields"] = redact_fields

    return config
