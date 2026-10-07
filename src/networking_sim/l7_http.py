import json
import re
from urllib.parse import urlparse
from typing import Any, Optional
from pydantic import BaseModel, Field

class UserRequest(BaseModel):
    method: str = Field(..., pattern="^(GET|POST|PUT|PATCH|DELETE)$")
    path: str
    protocol_version: str = "HTTP/1.1"
    host: str
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    accept: str = "*/*"
    content_type: Optional[str] = None
    body: Optional[Any] = None


def parse_input(input_str: str) -> UserRequest:
    input_str = input_str.strip()

    pattern = r'^(GET|POST|PUT|PATCH|DELETE)\s+([^\s]+)(?:\s+(.*))?$'
    match = re.match(pattern, input_str, re.IGNORECASE)
    if not match:
        raise ValueError(f"Invalid Input: '{input_str}'")

    method = match.group(1).upper()
    url = match.group(2)
    body_raw = match.group(3).strip() if match.group(3) else None

    if  not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    parsed_url = urlparse(url)
    host = parsed_url.netloc
    if not host: raise ValueError(f"Host is None")

    path = parsed_url.path if parsed_url.path else '/'
    if parsed_url.query:
        path += '?' + parsed_url.query 

    content_type = None
    body_parsed = None

    if body_raw:
        try:
            body_parsed = json.loads(body_raw)
            content_type = "application/json"
        except json.JSONDecodeError:
            body_parsed = body_raw
            content_type = "text/plain; charset=utf-8"

    return UserRequest(
        method=method,
        path=path,
        host=host,
        body=body_parsed,
        content_type=content_type
    )

# Request generation
def generate_request_json(req: UserRequest) -> str:
    return req.model_dump_json(indent=2)

def generate_raw_http_request(req: UserRequest) -> bytes:
    lines = [
        f"{req.method} {req.path} {req.protocol_version}",
        f"Host: {req.host}",
        f"User-Agent: {req.user_agent}",
        f"Accept: {req.accept}",
    ]

    body_bytes = b""
    if req.body is not None:
        ctype = req.content_type
        if ctype is None:
            ctype = "application/json" if isinstance(req.body, (dict, list)) else "text/plain; charset=utf-8"
        if ctype == "application/json":
            body_str = json.dumps(req.body, separators=(',', ':'))
        else:
            body_str = str(req.body)

        body_bytes = body_str.encode('utf-8')
        lines.append(f"Content-Type: {ctype}")
        lines.append(f"Content-Length: {len(body_bytes)}")

    headers_str = "\r\n".join(lines) + "\r\n\r\n"

    return headers_str.encode('utf-8') + body_bytes


# HTTP response generation
def recieve_byte_response():
    pass


# Reverse parsing
def parse_byte_response():
    pass


def generate_parsed_byte_response():
    pass


