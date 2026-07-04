#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGES = [
    ROOT / "packages" / "reconcile_engine",
    ROOT / "packages" / "reconcile_api_adapters",
    ROOT / "packages" / "reconcile_auth_adapters",
    ROOT / "packages" / "reconcile_core",
    ROOT / "demo" / "shared",
]
ROOT_PYPROJECT = ROOT / "pyproject.toml"
INTERNAL_PACKAGE_NAMES = (
    "reconcile-engine",
    "reconcile-api-adapters",
    "reconcile-auth-adapters",
    "reconcile-core",
    "reconcile-demo-shared",
)


def _read_version(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"', text, flags=re.MULTILINE)
    if not match:
        raise ValueError(f"version not found in {path}")
    return match.group(1)


def _sync_internal_dependency_pins(text: str, version: str) -> str:
    for package_name in INTERNAL_PACKAGE_NAMES:
        text = re.sub(
            rf'"{re.escape(package_name)}==[^"]+"',
            f'"{package_name}=={version}"',
            text,
        )
    return text


def _write_version(path: Path, version: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = re.sub(
        r'^version = "[^"]+"',
        f'version = "{version}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if path != ROOT_PYPROJECT:
        updated = _sync_internal_dependency_pins(updated, version)
    path.write_text(updated, encoding="utf-8")


def _bump_patch(version: str) -> str:
    major, minor, patch = version.split(".")
    return f"{major}.{minor}.{int(patch) + 1}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync Python package versions")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--bump-patch", action="store_true")
    parser.add_argument("--version")
    args = parser.parse_args()

    versions = {_read_version(ROOT_PYPROJECT): ROOT_PYPROJECT}
    for package in PACKAGES:
        versions[_read_version(package / "pyproject.toml")] = package / "pyproject.toml"

    unique_versions = set(versions.keys())
    if len(unique_versions) != 1:
        print("Version mismatch:")
        for version, path in versions.items():
            print(f"  {version}: {path}")
        return 1

    current = next(iter(unique_versions))

    if args.check:
        print(f"All package versions match: {current}")
        return 0

    target = _bump_patch(current) if args.bump_patch else args.version or current

    for path in [ROOT_PYPROJECT, *[package / "pyproject.toml" for package in PACKAGES]]:
        _write_version(path, target)

    print(f"Synced versions to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
