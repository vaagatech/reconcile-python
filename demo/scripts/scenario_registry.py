"""Backward-compatible re-export. Prefer ``snapline.demo_shared.scenario_registry``."""

from snapline.demo_shared.scenario_registry import (
    DOCS_URL,
    NODE_DOCS_URL,
    SCENARIO_META,
    SCENARIO_ORDER,
    ScenarioMeta,
    validate_scenario_registry,
)

__all__ = [
    "DOCS_URL",
    "NODE_DOCS_URL",
    "SCENARIO_META",
    "SCENARIO_ORDER",
    "ScenarioMeta",
    "validate_scenario_registry",
]
