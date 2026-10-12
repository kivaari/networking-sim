from .models import Segment

def segment(data: bytes, src_port: int, dst_port: int, seq0: int = 0, mss: int = 1460) -> list[Segment]:
    segs = []
    for offset in range(0, len(data), mss):
        chunk = data[offset:offset+mss]
        segs.append(Segment(
            src_port=src_port,
            dst_port=dst_port,
            seq=seq0+offset,
            ack=0,
            flags={"PSH", "ACK"},
            payload=chunk
        ))

    return segs

def reassemble(segs: list[Segment]) -> bytes:
    data = b''
    sorted_segs = sorted(segs, key=lambda seg:seg.seq)
    for seg in sorted_segs:
        data += seg.payload or b""
    return data

def handshake():
    pass

def checksum():
    pass