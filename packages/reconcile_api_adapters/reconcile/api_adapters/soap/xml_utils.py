from __future__ import annotations

import re
from typing import Any


def parse_soap_body(xml: str) -> dict[str, Any]:
    body_match = re.search(
        r"<(?:[\w]+:)?Body[^>]*>([\s\S]*?)</(?:[\w]+:)?Body>",
        xml,
        flags=re.IGNORECASE,
    )
    inner = body_match.group(1) if body_match else xml
    result: dict[str, Any] = {}

    tag_pattern = re.compile(
        r"<(?:[\w]+:)?(\w+)[^>]*>([^<]*)</(?:[\w]+:)?\1>",
        flags=re.IGNORECASE,
    )
    for match in tag_pattern.finditer(inner):
        key = match.group(1)
        value = (match.group(2) or "").strip()
        if key and value is not None:
            result[key] = value

    return result


def build_soap_envelope(body_inner_xml: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">'
        "<soap:Body>"
        f"{body_inner_xml}"
        "</soap:Body>"
        "</soap:Envelope>"
    )
