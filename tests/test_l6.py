from networking_sim.l6_presentation import encode, decode, compress, decompress


def test_encode_none():
    data, ct = encode(None)
    assert data == b""
    assert ct == "text/plain; charset=utf-8"


def test_encode_bytes():
    data, ct = encode(b"\x00\x01")
    assert data == b"\x00\x01"
    assert ct == "application/octet-stream"


def test_encode_dict_json():
    data, ct = encode({"a": 1})
    assert data == b'{"a":1}'
    assert ct == "application/json"


def test_encode_decode_roundtrip():
    payload = {"k": "v", "n": [1, 2, 3]}
    data, ct = encode(payload)
    assert decode(data, ct) == payload


def test_compress_small_passthrough():
    small = b"hello"
    assert compress(small) == small


def test_compress_large_shrinks():
    data = b"a" * 10000
    packed = compress(data)
    assert len(packed) < len(data)


def test_compress_decompress_roundtrip():
    data = (b"pattern" * 5000)
    assert decompress(compress(data)) == data


def test_decompress_uncompressed_passthrough():
    raw = b"not compressed at all" * 100
    assert decompress(raw) == raw