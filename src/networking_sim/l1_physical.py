from .models import Frame

def to_bits(frames: list[Frame]) -> str:
    # model_dump_json — компактный, без переносов; \n безопасен как разделитель
    payload = "\n".join(f.model_dump_json() for f in frames).encode('utf-8')
    return "".join(f"{b:08b}" for b in payload)

def from_bits(bits: str) -> list[Frame]:
    if len(bits) % 8 != 0:
        raise ValueError("bitstream is not byte-aligned")
    data = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))
    return [Frame.model_validate_json(line) for line in data.decode('utf-8').split("\n") if line]