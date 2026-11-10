import pytest
from networking_sim.models import Segment
from networking_sim.l3_ip import encapsulate, decapsulate
from networking_sim.l2_ethernet import frame, unframe
from networking_sim.l1_physical import to_bits, from_bits


def _segs(n=1, size=10):
    return [
        Segment(
            src_port=1, dst_port=2, seq=i, ack=0, 
            flags={"PSH", "ACK"}, payload=b"x"*size, checksum=120
        ) for i in range(n)
    ]


def test_l3_roundtrip():
    segs = _segs(3, 100)
    packets = encapsulate(segs, "1.1.1.1", "2.2.2.2")
    assert len(packets) == 3
    back = decapsulate(packets)
    assert [s.payload for s in back] == [s.payload for s in segs]


def test_l3_ttl_expired():
    packets = encapsulate(_segs(1), "1.1.1.1", "2.2.2.2", ttl=0)
    with pytest.raises(ValueError, match="TTL"):
        decapsulate(packets)


def test_l3_checksum_tamper():
    packets = encapsulate(_segs(1), "1.1.1.1", "2.2.2.2")
    packets[0].payload = b'{"tampered":true}'
    with pytest.raises(ValueError, match="checksum"):
        decapsulate(packets)


def test_l2_roundtrip():
    packets = encapsulate(_segs(2), "1.1.1.1", "2.2.2.2")
    frames = frame(packets, "aa:aa:aa:aa:aa:aa", "bb:bb:bb:bb:bb:bb")
    back = unframe(frames, expected_dst_mac="bb:bb:bb:bb:bb:bb")
    assert len(back) == 2


def test_l2_fcs_tamper():
    packets = encapsulate(_segs(1), "1.1.1.1", "2.2.2.2")
    frames = frame(packets, "aa", "bb")
    frames[0].payload = b"corrupted"
    with pytest.raises(ValueError, match="FCS"):
        unframe(frames, expected_dst_mac="bb")


def test_l2_wrong_mac_filtered():
    packets = encapsulate(_segs(1), "1.1.1.1", "2.2.2.2")
    frames = frame(packets, "aa", "bb")
    assert unframe(frames, expected_dst_mac="cc") == []


def test_l1_roundtrip():
    packets = encapsulate(_segs(2), "1.1.1.1", "2.2.2.2")
    frames = frame(packets, "aa", "bb")
    bits = to_bits(frames)
    assert set(bits) <= {"0", "1"}
    assert len(bits) % 8 == 0
    assert len(from_bits(bits)) == 2


def test_l1_bad_alignment():
    with pytest.raises(ValueError, match="byte-aligned"):
        from_bits("101")