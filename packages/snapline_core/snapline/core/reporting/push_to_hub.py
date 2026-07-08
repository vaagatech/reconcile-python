from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from .types import TestRunReport


def _normalize_hub_url(url: str) -> str:
    return url.rstrip("/")


def _parse_tags(value: str | None) -> list[str] | None:
    if not value or not value.strip():
        return None
    tags = sorted({t.strip().lower() for t in value.split(",") if t.strip()})
    return tags or None


def resolve_hub_config(argv: list[str] | None = None) -> dict[str, Any] | None:
    """Resolve hub URL from CLI (--hub-url) or env (SNAPLINE_HUB_URL)."""
    argv = argv if argv is not None else os.sys.argv

    cli_url: str | None = None
    cli_label: str | None = None
    cli_project: str | None = None
    cli_tags: str | None = None

    for index, arg in enumerate(argv):
        if arg.startswith("--hub-url="):
            cli_url = arg.split("=", 1)[1]
        elif arg == "--hub-url" and index + 1 < len(argv):
            cli_url = argv[index + 1]
        elif arg.startswith("--hub-label="):
            cli_label = arg.split("=", 1)[1]
        elif arg == "--hub-label" and index + 1 < len(argv):
            cli_label = argv[index + 1]
        elif arg.startswith("--hub-project="):
            cli_project = arg.split("=", 1)[1]
        elif arg == "--hub-project" and index + 1 < len(argv):
            cli_project = argv[index + 1]
        elif arg.startswith("--hub-tags="):
            cli_tags = arg.split("=", 1)[1]
        elif arg == "--hub-tags" and index + 1 < len(argv):
            cli_tags = argv[index + 1]

    hub_url = cli_url or os.environ.get("SNAPLINE_HUB_URL")
    if not hub_url:
        return None

    config: dict[str, Any] = {"hubUrl": hub_url}
    label = cli_label or os.environ.get("SNAPLINE_HUB_LABEL")
    project = cli_project or os.environ.get("SNAPLINE_HUB_PROJECT")
    tags = _parse_tags(cli_tags or os.environ.get("SNAPLINE_HUB_TAGS"))

    if label:
        config["label"] = label
    if project:
        config["project"] = project
    if tags:
        config["tags"] = tags
    return config


def push_test_report_to_hub(
    report: TestRunReport | dict[str, Any],
    *,
    hub_url: str | None = None,
    label: str | None = None,
    project: str | None = None,
    tags: list[str] | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Push a TestRunReport to Snapline Hub for centralized storage and UI viewing."""
    resolved = config or {}
    url = hub_url or resolved.get("hubUrl")
    if not url:
        raise ValueError("hub_url is required (or pass config from resolve_hub_config)")

    resolved_label = label or resolved.get("label")
    resolved_project = project or resolved.get("project")
    resolved_tags = tags or resolved.get("tags")
    hub_url_normalized = _normalize_hub_url(url)

    payload = dict(report)
    if resolved_label:
        payload["label"] = resolved_label
    if resolved_project:
        payload["project"] = resolved_project
    if resolved_tags:
        payload["tags"] = resolved_tags

    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{hub_url_normalized}/api/reports",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Snapline Hub push failed ({exc.code}): {error_body}") from exc

    return {
        "id": result["id"],
        "url": f"{hub_url_normalized}{result['url']}",
    }
