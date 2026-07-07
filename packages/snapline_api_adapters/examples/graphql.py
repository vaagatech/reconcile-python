"""GraphQL API adapter example."""
from snapline.api_adapters import api, execute_api

result = execute_api(
    api.graphql(
        {
            "endpoint": "https://countries.trevorblades.com/graphql",
            "query": "query { country(code: \"US\") { name capital } }",
            "dataPath": "country",
        }
    )
)

print("GraphQL data:", result["data"])
