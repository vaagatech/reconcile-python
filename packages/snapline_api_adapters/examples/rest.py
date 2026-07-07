"""REST API adapter example."""
from snapline.api_adapters import api, execute_api

result = execute_api(
    api.rest(
        {
            "endpoint": "https://jsonplaceholder.typicode.com/users/1",
            "method": "GET",
        }
    )
)

print("REST status:", result["status"])
print("REST data:", result["data"])
