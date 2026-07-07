# snapline-auth-adapters

Pluggable authentication adapters for Snapline test automation. Initialize OAuth2, OpenID, or Basic Auth credentials and receive ready-to-use HTTP headers.

## Install

```bash
pip install snapline-auth-adapters
```

## Quick start

```python
import asyncio
from snapline.auth_adapters import auth

async def main():
    adapter = auth.basic({"username": "user", "password": "secret"})
    result = await adapter.initialize()
    print(result["headers"])

asyncio.run(main())
```

## Documentation

**https://vaagatech.github.io/snapline-python/** · [Node.js docs](https://vaagatech.github.io/snapline/)
