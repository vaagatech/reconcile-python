"""Basic Snapline engine usage."""
from snapline.engine import snapline

live_response = {
    "id": "usr_001",
    "email": "alice@example.com",
    "status": "synced",
    "currentdate": "2026-01-15T10:00:00.000Z",
    "pincode": "482910",
}

expected = {
    "id": "usr_001",
    "email": "alice@example.com",
    "status": "synced",
    "currentdate": "VALID_DATE",
}


def _valid_date(value, _key=None, _parent=None):
    if isinstance(value, str):
        try:
            from datetime import datetime

            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return "VALID_DATE"
        except ValueError:
            pass
    return "INVALID_DATE"


result = snapline(
    live_response,
    expected,
    {
        "ignoreFields": ["pincode"],
        "transformations": {"currentdate": _valid_date},
    },
)

print("PASS" if result["match"] else "FAIL")
if result.get("diff"):
    import json

    print(json.dumps(result["diff"], indent=2))
