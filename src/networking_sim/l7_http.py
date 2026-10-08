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

class RawHTTPResponse(BaseModel):
    protocol_version: str = Field(..., pattern="^(HTTP/1.1|HTTP/2)")
    status: str
    content_type: Optional[str] = None
    content_length: Optional[str] = None
    connection: Optional[str] = None
    server: Optional[str] = None
    date: Optional[str] = None
    body: Optional[Any] = None

DNS_TABLE = {"example.com": "162.21.12.12", "api.example.com": "192.32.34.45", "api.test.com": "192.23.54.76", "localhost": "192.0.0.1"}
CACHE = {}

def resolve(host: str) -> str: #DNS Resolver like thing
    host = host.lower()
    if host in CACHE: return CACHE[host]
    if host not in DNS_TABLE: raise ValueError(f"NXDOMAIN: {host}")
    CACHE[host] = DNS_TABLE[host]
    return CACHE[host]

def parse_input(input_str: str) -> UserRequest:
    input_str = input_str.strip()

    pattern = r'^(GET|POST|PUT|PATCH|DELETE)\s+([^\s]+)(?:\s+(.*))?$'
    match = re.match(pattern, input_str, re.IGNORECASE)
    if not match:
        raise ValueError(f"Invalid Input: '{input_str}'")

    method = match.group(1).upper()
    url = match.group(2)
    body_raw = match.group(3).strip() if match.group(3) else None

    if not url.startswith(('http://', 'https://')): url = 'http://' + url

    parsed_url = urlparse(url)
    host = parsed_url.hostname.lower() if parsed_url.hostname else ""
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
def received_bytes_parse(received_bytes: bytes) -> RawHTTPResponse:
    header_part, body_part = received_bytes.split(b'\r\n\r\n', 1)
    lines = header_part.split(b'\r\n')
    headers = {}
    for line in lines[1:]:
        key, value = line.split(b':', 1)
        headers[key.strip().lower().decode('utf-8')] = value.strip().decode('utf-8')

    ctype = (headers.get('content-type') or '').split(';', 1)[0].strip()
    if ctype == 'application/json':
        body = json.loads(body_part)
    else:
        body = body_part.decode('utf-8')

    protocol, s = lines[0].strip().decode('utf-8').split(' ', 1)

    return RawHTTPResponse(
        protocol_version=protocol,
        status=s,
        content_type=headers.get('content-type'),
        content_length=headers.get('content-length'),
        connection=headers.get('connection'),
        server=headers.get('server'),
        date=headers.get('date'),
        body=body
    )