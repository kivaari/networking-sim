from .models import Segment, Packet

def checksum(src_ip: str, dst_ip: str, ttl: int, payload: bytes) -> int:
    data = f"{src_ip}|{dst_ip}|{ttl}|".encode('utf-8') + payload
    return sum(data) % 65535

def encapsulate(segs: list[Segment], src_ip: str, dst_ip: str, ttl: int = 64) -> list[Packet]:
    packets = []
    for seg in segs:
        payload = seg.model_dump_json().encode('utf-8')
        packets.append(Packet(
            src_ip=src_ip,
            dst_ip=dst_ip,
            ttl=ttl,
            protocol="TCP",
            payload=payload,
            header_checksum=checksum(src_ip, dst_ip, ttl, payload),
        ))
    return packets

def decapsulate(packets: list[Packet]) -> list[Segment]:
    segs = []
    for pkt in packets:
        if pkt.ttl <= 0:
            raise ValueError("TTL expired")
        if checksum(pkt.src_ip, pkt.dst_ip, pkt.ttl, pkt.payload) != pkt.header_checksum:
            raise ValueError("IP header checksum mismatch")
        segs.append(Segment.model_validate_json(pkt.payload))
    return segs