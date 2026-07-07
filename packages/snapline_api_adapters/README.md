# snapline-api-adapters

REST, GraphQL, and SOAP API adapters for Snapline — file-driven test requests with a single execution interface.

## Install

```bash
pip install snapline-api-adapters
```

## Quick start

```python
from snapline.api_adapters import api, execute_api

config = api.rest({
    "baseUrl": "https://api.example.com",
    "endpoint": "/users",
    "method": "GET",
})
response = execute_api(config)
print(response)
```

## Documentation

**https://vaagatech.github.io/snapline-python/** · [Node.js docs](https://vaagatech.github.io/snapline/)
