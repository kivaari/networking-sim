import json

def handle_http_request(raw: bytes) -> bytes:
    header, _, body = raw.partition(b'\r\n\r\n')
    request_line = header.split(b'\r\n', 1)[0].decode('utf-8')
    method, path, *_ = request_line.split(' ')

    resp_body = json.dumps({
        "status": "ok",
        "method": method,
        "path": path,
        "received_bytes": len(raw),
    }).encode('utf-8')

    return (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: application/json\r\n"
        + f"Content-Length: {len(resp_body)}\r\n".encode()
        + b"Connection: keep-alive\r\n"
        + b"Server: NetworkingSim/1.0\r\n"
        + b"Date: Mon, 10 Nov 2026 12:00:00 GMT\r\n"
        + b"\r\n"
        + resp_body
    )