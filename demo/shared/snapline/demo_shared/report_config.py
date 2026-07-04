from __future__ import annotations

import json
import os
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Literal

ReportFormat = Literal["json", "html", "text"]


def resolve_report_config(argv: list[str] | None = None) -> dict[str, Any] | None:
    parser = ArgumentParser(add_help=False)
    parser.add_argument("--report-format", choices=["json", "html", "text"])
    parser.add_argument("--report-output")
    args, _ = parser.parse_known_args(argv)

    report_format = args.report_format or os.environ.get("REPORT_FORMAT")
    report_output = args.report_output or os.environ.get("REPORT_OUTPUT")

    if not report_format or not report_output:
        return None

    return {"format": report_format, "outputPath": report_output}
