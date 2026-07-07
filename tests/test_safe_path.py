from __future__ import annotations

import pytest
from snapline.engine.io.safe_path import assert_within_root


def test_assert_within_root_allows_files_under_root(tmp_path):
    root = tmp_path / "fixtures"
    root.mkdir()
    allowed = root / "cases" / "a" / "case.json"
    allowed.parent.mkdir(parents=True)
    allowed.write_text("{}", encoding="utf-8")

    resolved = assert_within_root(root, allowed)
    assert resolved == allowed.resolve()


def test_assert_within_root_rejects_path_traversal(tmp_path):
    root = tmp_path / "fixtures"
    root.mkdir()
    outside = tmp_path / "secret.txt"
    outside.write_text("secret", encoding="utf-8")

    with pytest.raises(ValueError, match="escapes allowed root"):
        assert_within_root(root, outside)

    with pytest.raises(ValueError, match="escapes allowed root"):
        assert_within_root(root, root / ".." / "secret.txt")
