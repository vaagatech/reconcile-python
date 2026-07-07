"""SOAP API adapter example."""
from snapline.api_adapters import api, execute_api

envelope = (
    '<?xml version="1.0"?>'
    '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">'
    "<soap:Body><GetUserRequest><email>alice@example.com</email></GetUserRequest></soap:Body>"
    "</soap:Envelope>"
)

result = execute_api(
    api.soap(
        {
            "endpoint": "https://example.com/soap/user",
            "soapAction": "GetUser",
            "envelope": envelope,
        }
    )
)

print("SOAP parsed data:", result["data"])
