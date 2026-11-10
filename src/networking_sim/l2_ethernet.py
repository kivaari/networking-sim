import zlib
from .models import Packet, Frame

def crc32(data: bytes) -> int:
    return zlib.crc32(data) & 0xFFFFFFFF

def frame(packets: list[Packet], src_mac: str, dst_mac: str, ethertype: int = 0x0800) -> list[Frame]:
    frames = []
    for pkt in packets:
        payload = pkt.model_dump_json().encode('utf-8')
        frames.append(Frame(
            src_mac=src_mac,
            dst_mac=dst_mac,
            ethertype=ethertype,
            payload=payload,
            fcs=crc32(payload),
        ))
    return frames

def unframe(frames: list[Frame], expected_dst_mac: str) -> list[Packet]:
    packets = []
    for f in frames:
        if crc32(f.payload) != f.fcs:
            raise ValueError("FCS mismatch")
        if f.dst_mac.lower() != expected_dst_mac.lower():
            continue  # чужой кадр — отбрасываем
        packets.append(Packet.model_validate_json(f.payload))
    return packets