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
            payload=chunk,
            checksum=checksum(chunk)
        ))

    return segs

def reassemble(segs: list[Segment]) -> bytes:
    data = b''
    sorted_segs = sorted(segs, key=lambda seg:seg.seq)
    for seg in sorted_segs:
        payload = seg.payload or b""
        if checksum(payload) != seg.checksum:
            raise ValueError("corrupted")
        data += payload
    return data

def handshake(src, dst) -> dict:
    print(f"request to: {dst}, from: {src}, SYN seq=1000\n")
    print(f"response to: {src}, from: {dst}, SYN-ACK seq=5000 ack=1001")
    print(f"response to: {dst}, from {src}, ACK ack=5001")
    seq = 1001
    return {"seq0":seq, "state": "ESTABLISHED"}

def checksum(payload: bytes) -> int:
    return sum(payload) % 65535