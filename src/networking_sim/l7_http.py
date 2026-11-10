import json
import re
from urllib.parse import urlparse
from .models import UserRequest, RawHTTPResponse


def parse_input(input_str: str) -> UserRequest:
    input_str = input_str.strip()

    pattern = r'^(GET|POST|PUT|PATCH|DELETE)\s+([^\s]+)(?:\s+(.*))?$'
    match = re.match(pattern, input_str, re.IGNORECASE)
    if not match:
        raise ValueError(f"Invalid input: '{input_str}'")

    method = match.group(1).upper()
    url = match.group(2)
    body_raw = match.group(3).strip() if match.group(3) else None
    
    if body_raw and body_raw.upper() in ("HTTP/1.1", "HTTP/1.0", "HTTP/2"):
        body_raw = None

    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    parsed = urlparse(url)
    host = parsed.hostname.lower() if parsed.hostname else ""
    if not host:
        raise ValueError("Host is None")

    path = parsed.path or '/'
    if parsed.query:
        path += '?' + parsed.query

    content_type, body = None, None
    if body_raw:
        try:
            body = json.loads(body_raw)
            content_type = "application/json"
        except json.JSONDecodeError:
            body = body_raw
            content_type = "text/plain; charset=utf-8"

    return UserRequest(
        method=method,
        path=path,
        host=host,
        body=body,
        content_type=content_type,
    )


def generate_raw_http_request(req: UserRequest) -> bytes:
    lines = [
        f"{req.method} {req.path} {req.protocol_version}",
        f"Host: {req.host}",
        f"User-Agent: {req.user_agent}",
        f"Accept: {req.accept}",
    ]

    body_bytes = b""
    if req.body is not None:
        ctype = req.content_type or (
            "application/json" if isinstance(req.body, (dict, list))
            else "text/plain; charset=utf-8"
        )
        if ctype.startswith("application/json"):
            body_bytes = json.dumps(req.body, separators=(',', ':')).encode('utf-8')
        else:
            body_bytes = str(req.body).encode('utf-8')

        lines.append(f"Content-Type: {ctype}")
        lines.append(f"Content-Length: {len(body_bytes)}")

    return ("\r\n".join(lines) + "\r\n\r\n").encode('utf-8') + body_bytes


def received_bytes_parse(received_bytes: bytes) -> RawHTTPResponse:
    header_part, body_part = received_bytes.split(b'\r\n\r\n', 1)
    lines = header_part.split(b'\r\n')

    headers: dict[str, str] = {}
    for line in lines[1:]:
        key, value = line.split(b':', 1)
        headers[key.strip().lower().decode('utf-8')] = value.strip().decode('utf-8')

    base_ctype = (headers.get('content-type') or '').split(';', 1)[0].strip()
    if base_ctype == 'application/json':
        body = json.loads(body_part)
    else:
        body = body_part.decode('utf-8')

    protocol, status = lines[0].strip().decode('utf-8').split(' ', 1)

    return RawHTTPResponse(
        protocol_version=protocol,
        status=status,
        content_type=headers.get('content-type'),
        content_length=headers.get('content-length'),
        connection=headers.get('connection'),
        server=headers.get('server'),
        date=headers.get('date'),
        body=body,
    )