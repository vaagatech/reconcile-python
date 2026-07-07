from __future__ import annotations

from snapline.engine import snapline


def test_snapline_matches_identical_data():
    live = {"id": 1, "name": "Ada"}
    expected = {"id": 1, "name": "Ada"}

    result = snapline(live, expected)

    assert result["match"] is True
    assert result["diff"] is None


def test_snapline_strips_ignore_fields_before_compare():
    live = {"id": 1, "updatedAt": "2026-01-01"}
    expected = {"id": 1}

    result = snapline(live, expected, {"ignoreFields": ["updatedAt"]})

    assert result["match"] is True
    assert "updatedAt" not in result["processed"]


def test_snapline_applies_transformations():
    live = {"amount": "10.5"}
    expected = {"amount": 10.5}

    result = snapline(
        live,
        expected,
        {"transformations": {"amount": lambda value, _key, _parent: float(value)}},
    )

    assert result["match"] is True
    assert result["processed"]["amount"] == 10.5
