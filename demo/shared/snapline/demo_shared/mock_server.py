from __future__ import annotations

import html
import json
import random
import re
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

from snapline.api_adapters import build_soap_envelope

from .demo_domain import demo_domain, volatile_pincode, volatile_trace_id
from .graphql_schema import _to_iso_string, execute_demo_graphql

MAX_BODY_BYTES = 1_048_576
PORT = 0


@dataclass
class MockServerHandle:
    server: HTTPServer
    thread: threading.Thread
    base_url: str


class _MockHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _read_body(self) -> str:
        try:
            length = int(self.headers.get("Content-Length", 0))
        except ValueError:
            length = 0
        if length <= 0:
            return ""
        if length > MAX_BODY_BYTES:
            raise ValueError("Request body too large")
        return self.rfile.read(length).decode("utf-8")

    def _send_json(self, status: int, payload: Any) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/oauth/token":
            self._read_body()
            self._send_json(
                200,
                {
                    "access_token": "mock-oauth-token-abc123",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                },
            )
            return

        if path == "/api/v1/user/sync":
            body = self._read_body()
            auth_header = self.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                self._send_json(401, {"error": "Unauthorized"})
                return

            try:
                payload = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self._send_json(400, {"error": "Invalid JSON"})
                return

            self._send_json(
                200,
                {
                    "id": payload.get("id", "usr_001"),
                    "email": payload.get("email", demo_domain.email),
                    "status": demo_domain.api_status,
                    "currentdate": datetime.now(timezone.utc).isoformat(),
                    "pincode": volatile_pincode(),
                },
            )
            return

        if path == "/graphql":
            body = self._read_body()
            auth_header = self.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                self._send_json(401, {"errors": [{"message": "Unauthorized"}]})
                return

            try:
                parsed_body = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self._send_json(400, {"errors": [{"message": "Invalid JSON"}]})
                return

            query = parsed_body.get("query", "")
            variables = parsed_body.get("variables", {})
            result = execute_demo_graphql(query, variables)

            if result.get("errors"):
                self._send_json(400, {"errors": result["errors"]})
                return

            self._send_json(200, {"data": result.get("data")})
            return

        if path == "/soap/user":
            body = self._read_body()
            email_match = re.search(r"<email>([^<]+)</email>", body, flags=re.IGNORECASE)
            email = html.escape(email_match.group(1) if email_match else demo_domain.email)

            response_xml = build_soap_envelope(
                f"<GetUserResponse><email>{email}</email>"
                f"<status>{demo_domain.api_status}</status>"
                f"<role>{demo_domain.role}</role></GetUserResponse>"
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/xml; charset=utf-8")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(response_xml.encode("utf-8"))
            return

        self._send_json(404, {"error": "Not found"})

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/api/v1/users/profile":
            email = query.get("email", [demo_domain.email])[0]
            self._send_json(
                200,
                {
                    "email": email,
                    "status": demo_domain.api_status,
                    "role": demo_domain.role,
                    "currentdate": datetime.now(timezone.utc).isoformat(),
                    "traceId": volatile_trace_id(),
                },
            )
            return

        if path == "/api/v1/users/enriched":
            email = query.get("email", [demo_domain.email])[0]
            self._send_json(
                200,
                {
                    "email": email,
                    "role": demo_domain.role,
                    "tier": demo_domain.tier,
                    "lastLogin": _to_iso_string(demo_domain.last_login),
                },
            )
            return

        if path == "/api/v1/events/tracked":
            self._send_json(
                200,
                {
                    "email": demo_domain.email,
                    "status": "delivered",
                    "metadata": {
                        "trackedAt": datetime.now(timezone.utc).isoformat(),
                        "requestId": f"req_{random.randint(0, 999_999)}",
                    },
                },
            )
            return

        self._send_json(404, {"error": "Not found"})


def create_mock_server() -> MockServerHandle:
    server = HTTPServer(("127.0.0.1", PORT), _MockHandler)
    server.socket.settimeout(30)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    return MockServerHandle(server=server, thread=thread, base_url=f"http://{host}:{port}")


def close_mock_server(handle: MockServerHandle) -> None:
    handle.server.shutdown()
    handle.server.server_close()
    handle.thread.join(timeout=5)
