import pytest
import json
from pydantic import ValidationError


from networking_sim import (
    UserRequest,
    parse_input,
    generate_request_json,
    generate_raw_http_request
)

@pytest.mark.parametrize("input_str, expected_method, expected_host, expected_path, expected_body_type, expected_content_type", [
    # Базовый GET
    (
        "GET example.com/orders/1",
        "GET", "example.com", "/orders/1", type(None), None
    ),
    # POST с валидным JSON
    (
        'POST https://api.test.com/v1/users {"id": 123, "name": "test"}',
        "POST", "api.test.com", "/v1/users", dict, "application/json"
    ),
    # POST с грязным JSON
    (
        'POST example.com/data {productId: "3fadasdasda", qty: 2}',
        "POST", "example.com", "/data", str, "text/plain; charset=utf-8"
    ),
    # URL с query-параметрами
    (
        "GET example.com/search?q=python&page=2",
        "GET", "example.com", "/search?q=python&page=2", type(None), None
    ),
    # PUT запрос с текстовым телом
    (
        "PUT example.com/update plain text body",
        "PUT", "example.com", "/update", str, "text/plain; charset=utf-8"
    ),
])

def test_parse_input_success(
    input_str, expected_method, expected_host, expected_path, expected_body_type, expected_content_type
):
    req = parse_input(input_str)
    
    assert req.method == expected_method
    assert req.host == expected_host
    assert req.path == expected_path
    assert isinstance(req.body, expected_body_type)
    assert req.content_type == expected_content_type
    assert req.protocol_version == "HTTP/1.1"


@pytest.mark.parametrize("invalid_input", [
    "Это просто текст",
    "CONNECT example.com",
    "GET",
    "POST",
])

def test_parse_input_invalid_format(invalid_input):
    with pytest.raises(ValueError, match="Неверный формат строки|Invalid Input"):
        parse_input(invalid_input)


def test_user_request_validation_failure():
    with pytest.raises(ValidationError) as exc_info:
        UserRequest(
            method="INVALID_METHOD",
            path="/test",
            host="example.com"
        )
    
    assert "pattern" in str(exc_info.value).lower() or "string does not match regex" in str(exc_info.value).lower()


def test_generate_request_json():
    req = UserRequest(
        method="GET",
        path="/api/v1",
        host="example.com",
        user_agent="TestAgent"
    )
    
    json_str = generate_request_json(req)
    parsed_dict = json.loads(json_str)
    
    assert parsed_dict["method"] == "GET"
    assert parsed_dict["host"] == "example.com"
    assert parsed_dict["user_agent"] == "TestAgent"
    assert "body" in parsed_dict


def test_generate_raw_http_no_body():
    req = UserRequest(method="GET", path="/health", host="localhost")
    raw_bytes = generate_raw_http_request(req)

    assert isinstance(raw_bytes, bytes)
    
    raw_str = raw_bytes.decode('utf-8')

    assert raw_str.startswith("GET /health HTTP/1.1\r\n")

    assert "Host: localhost\r\n" in raw_str
    assert "User-Agent:" in raw_str

    assert raw_str.endswith("\r\n\r\n")
    assert "Content-Length" not in raw_str


def test_generate_raw_http_with_dict_body():
    req = UserRequest(
        method="POST",
        path="/users",
        host="api.example.com",
        body={"name": "Alice", "age": 30}
    )
    raw_bytes = generate_raw_http_request(req)
    raw_str = raw_bytes.decode('utf-8')
    
    assert "Content-Type: application/json\r\n" in raw_str

    assert "Content-Length: 25\r\n" in raw_str

    assert "\r\n\r\n" in raw_str
    header_part, body_part = raw_str.split("\r\n\r\n", 1)