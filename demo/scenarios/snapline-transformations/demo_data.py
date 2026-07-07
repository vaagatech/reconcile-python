from __future__ import annotations

from datetime import datetime
from typing import Any


def _valid_date(value: Any, _key=None, _parent=None) -> str:
    if isinstance(value, str):
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return "VALID_DATE"
        except ValueError:
            pass
    return "INVALID_DATE"


role_transform = {"role": lambda value, _key=None, _parent=None: str(value).upper()}
tier_transform = {"tier": lambda value, _key=None, _parent=None: str(value).upper()}
date_transform = {"lastLogin": _valid_date, "renewsAt": _valid_date}

enrichment_transforms = {**role_transform, **tier_transform, **date_transform}
role_tier_only_transforms = {**role_transform, **tier_transform}
date_field_transforms = {
    "lastLogin": date_transform["lastLogin"],
    "renewsAt": date_transform["renewsAt"],
}
