"""Basic reconcile example."""
from reconcile.engine import reconcile

live = {"email": "alice@example.com", "status": "synced", "pincode": "123456"}
expected = {"email": "alice@example.com", "status": "synced"}

result = reconcile(
    live,
    expected,
    {
        "ignoreFields": ["pincode"],
        "transformations": {
            "status": lambda value, _key=None, _parent=None: str(value).upper(),
        },
    },
)

print("match:", result["match"])
print("diff:", result["diff"])
