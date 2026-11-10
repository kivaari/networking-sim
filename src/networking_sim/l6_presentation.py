import json
import gzip
import json

_COMPRESS_MARK = b"L6Z\x01"
_MIN_COMPRESS_SIZE = 128 

def encode(payload: str | dict | list | bytes | None) -> tuple[bytes, str]:
    if payload is None: return b"", "text/plain; charset=utf-8"
    if isinstance(payload, bytes): return payload, "application/octet-stream"
    if isinstance(payload, (dict, list)): 
        return json.dumps(payload, separators=(',',':')).encode('utf-8'), "application/json"
    return str(payload).encode('utf-8'), "text/plain; charset=utf-8"

def decode(data: bytes, ctype: str) -> str | dict:
    base = (ctype or '').split(';', 1)[0].strip()
    if base == "application/json": return json.loads(data.decode('utf-8'))
    if base == "application/octet-stream": return data
    return data.decode("utf-8")

def compress(data: bytes, min_size: int = _MIN_COMPRESS_SIZE) -> bytes:
    if not data or len(data) < min_size:
        return data
    packed = gzip.compress(data, mtime=0)
    if len(packed) + len(_COMPRESS_MARK) >= len(data):
        return data
    return _COMPRESS_MARK + packed

def decompress(data: bytes) -> bytes:
    if not data.startswith(_COMPRESS_MARK):
        return data
    return gzip.decompress(data[len(_COMPRESS_MARK):])