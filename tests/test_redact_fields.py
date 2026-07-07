from __future__ import annotations

from snapline.core.reporting.redact_fields import redact_fields, redact_suite_results


def test_redact_fields_replaces_top_level_values():
    data = {"token": "secret", "status": "ok"}

    redacted = redact_fields(data, ["token"])

    assert redacted == {"token": "[REDACTED]", "status": "ok"}
    assert data["token"] == "secret"


def test_redact_fields_supports_nested_paths():
    data = {"user": {"email": "ada@example.com"}, "status": "ok"}

    redacted = redact_fields(data, ["user.email"])

    assert redacted["user"]["email"] == "[REDACTED]"
    assert redacted["status"] == "ok"


def test_redact_suite_results_redacts_each_step():
    suites = [
        {
            "name": "api",
            "passed": True,
            "results": [
                {"step": "case-1", "passed": True, "data": {"token": "abc"}},
            ],
        }
    ]

    redacted = redact_suite_results(suites, ["data"])

    assert redacted[0]["results"][0]["data"] == "[REDACTED]"
    assert suites[0]["results"][0]["data"]["token"] == "abc"
