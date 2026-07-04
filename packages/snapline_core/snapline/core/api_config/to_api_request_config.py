from __future__ import annotations

import re
from typing import Any

from ..types import ApiFileTestConfig, ApiRequestConfig


def to_api_request_config(config: ApiFileTestConfig | dict[str, Any]) -> ApiRequestConfig:
    protocol = config.get("protocol")

    if protocol == "soap":
        return {
            "protocol": "soap",
            "endpoint": config.get("endpoint", "/"),
            "soapAction": config.get("soapAction"),
            "envelope": config.get("envelope"),
            "inputFile": config.get("inputFile"),
            "headers": config.get("headers"),
        }

    if protocol == "graphql":
        return {
            "protocol": "graphql",
            "endpoint": config.get("endpoint", "/graphql"),
            "query": config.get("query"),
            "queryFile": config.get("queryFile"),
            "variables": config.get("variables"),
            "variablesFile": config.get("variablesFile"),
            "inputFile": config.get("inputFile"),
            "dataPath": config.get("dataPath"),
            "headers": config.get("headers"),
        }

    return {
        "protocol": "rest",
        "endpoint": config.get("endpoint", "/"),
        "method": config.get("method"),
        "inputFile": config.get("inputFile"),
        "body": config.get("body"),
        "headers": config.get("headers"),
    }
