from networking_sim.l6_presentation import encode, decode, compress, decompress


def test_encode_dict():
    data, ctype = encode({"a": 1})
    assert ctype == "application/json"
    assert data == b'{"a":1}'


def test_encode_list():
    data, ctype = encode([1, 2])
    assert ctype == "application/json"
    assert data == b'[1,2]'


def test_encode_str():
    data, ctype = encode("hi")
    assert ctype == "text/plain; charset=utf-8"
    assert data == b"hi"


def test_encode_none():
    data, ctype = encode(None)
    assert data == b""
    assert ctype == "text/plain; charset=utf-8"


def test_encode_bytes_passthrough():
    data, ctype = encode(b"\x00\x01")
    assert data == b"\x00\x01"
    assert ctype == "application/octet-stream"


def test_decode_json():
    assert decode(b'{"a":1}', "application/json") == {"a": 1}


def test_decode_json_with_charset():
    assert decode(b'{"a":1}', "application/json; charset=utf-8") == {"a": 1}


def test_decode_text():
    assert decode("привет".encode("utf-8"), "text/plain; charset=utf-8") == "привет"


def test_decode_octet_stream():
    assert decode(b"\x00\x01", "application/octet-stream") == b"\x00\x01"


def test_roundtrip_cyrillic():
    payload = {"a": "привет"}
    data, ctype = encode(payload)
    assert decode(data, ctype) == payload


def test_compress_passthrough():
    assert compress(b"hi") == b"hi"
    assert decompress(b"hi") == b"hi"
