import json

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

def compress(data):
    return data

def decompress(data):
    return data