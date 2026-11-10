import pytest
from networking_sim.l7_http import (
    parse_input, generate_raw_http_request, received_bytes_parse,
)
from networking_sim.models import UserRequest


def test_parse_get():
    req = parse_input("GET http://example.com/api HTTP/1.1")
    assert req.method == "GET"
    assert req.host == "example.com"
    assert req.path == "/api"
    assert req.body is None


def test_parse_with_query():
    req = parse_input("GET example.com/search?q=os&page=2")
    assert req.path == "/search?q=os&page=2"


def test_parse_post_json():
    req = parse_input('POST example.com/api {"name":"alice"}')
    assert req.method == "POST"
    assert req.body == {"name": "alice"}
    assert req.content_type == "application/json"


def test_parse_post_text():
    req = parse_input("POST example.com/api plain text")
    assert req.body == "plain text"
    assert req.content_type.startswith("text/plain")


def test_parse_invalid_raises():
    with pytest.raises(ValueError, match="Invalid input"):
        parse_input("INVALID REQUEST")


def test_parse_empty_host_raises():
    with pytest.raises(ValueError, match="Host is None"):
        parse_input("GET /path")


def test_generate_raw_request():
    req = UserRequest(method="GET", path="/", host="example.com")
    raw = generate_raw_http_request(req)
    assert raw.startswith(b"GET / HTTP/1.1\r\n")
    assert b"Host: example.com\r\n" in raw
    assert raw.endswith(b"\r\n\r\n")


def test_generate_with_body_sets_content_length():
    req = UserRequest(
        method="POST", path="/api", host="example.com",
        body={"n": 1}, content_type="application/json",
    )
    raw = generate_raw_http_request(req)
    body = raw.split(b"\r\n\r\n", 1)[1]
    assert body == b'{"n":1}'
    assert f"Content-Length: {len(body)}".encode() in raw


def test_received_bytes_parse_roundtrip():
    raw = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: application/json\r\n"
        b"Content-Length: 15\r\n"
        b"Server: Test/1.0\r\n"
        b"\r\n"
        b'{"status":"ok"}'
    )
    resp = received_bytes_parse(raw)
    assert resp.protocol_version == "HTTP/1.1"
    assert resp.status == "200 OK"
    assert resp.body == {"status": "ok"}
    assert resp.server == "Test/1.0"