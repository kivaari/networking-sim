import pytest
from networking_sim.l4_tcp import segment, reassemble, handshake, checksum


def test_segment_split():
    data = b"A" * 3000
    segs = segment(data, src_port=54321, dst_port=80)
    assert len(segs) == 3
    assert [s.seq for s in segs] == [0, 1460, 2920]
    assert [len(s.payload) for s in segs] == [1460, 1460, 80]
    assert all(s.src_port == 54321 and s.dst_port == 80 for s in segs)
    assert all(s.flags == {"PSH", "ACK"} for s in segs)


def test_segment_custom_seq0_mss():
    data = b"0123456789"
    segs = segment(data, src_port=1, dst_port=80, seq0=1001, mss=4)
    assert [s.seq for s in segs] == [1001, 1005, 1009]
    assert b"".join(s.payload for s in segs) == data


def test_segment_empty():
    assert segment(b"", 1, 80) == []


def test_reassemble_roundtrip():
    data = b"B" * 5000
    segs = segment(data, 1, 80)
    assert reassemble(segs) == data


def test_reassemble_shuffled():
    data = b"C" * 3000
    segs = segment(data, 1, 80)
    assert reassemble(segs[::-1]) == data


def test_reassemble_corrupted():
    data = b"hello"
    segs = segment(data, 1, 80)
    segs[0].payload = b"HELLO"
    with pytest.raises(ValueError, match="corrupted"):
        reassemble(segs)


def test_checksum():
    assert checksum(b"") == 0
    assert checksum(b"\x01\x02") == 3
    assert checksum(b"hello") == sum(b"hello") % 65535


def test_handshake():
    out = handshake("me", "srv")
    assert out["state"] == "ESTABLISHED"
    assert out["seq0"] == 1001
