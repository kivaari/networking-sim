import main as m
from networking_sim.l6_presentation import decompress
from networking_sim.l7_http import received_bytes_parse


def test_full_pipeline_post_json():
    m._wire_buffer = b""
    m.output_request('POST example.com/api {"name":"alice"}')

    assert m._wire_buffer, "сервер не вернул ответ"
    response = received_bytes_parse(decompress(m._wire_buffer))

    assert response.protocol_version == "HTTP/1.1"
    assert response.status.startswith("200")
    assert isinstance(response.body, dict)
    assert response.body["method"] == "POST"
    assert response.body["path"] == "/api"


def test_full_pipeline_get():
    m._wire_buffer = b""
    m.output_request("GET localhost/health")
    response = received_bytes_parse(decompress(m._wire_buffer))
    assert response.body["method"] == "GET"
    assert response.body["path"] == "/health"


def test_full_pipeline_large_body():
    """Тело больше MSS — проверяем многократную сегментацию по всему стеку."""
    m._wire_buffer = b""
    big = "x" * 5000
    m.output_request(f"POST example.com/api {big}")
    response = received_bytes_parse(decompress(m._wire_buffer))
    assert response.body["received_bytes"] > 5000