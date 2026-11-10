from networking_sim.models import RawHTTPResponse
from networking_sim.l7_http import (
    parse_input,
    generate_raw_http_request,
    received_bytes_parse,
)
from networking_sim.l6_presentation import encode, compress, decompress
from networking_sim.resolve import resolve
from networking_sim.l5_session import get_or_create
from networking_sim.l4_tcp import segment, reassemble, handshake
from networking_sim.l3_ip import encapsulate as ip_encapsulate, decapsulate as ip_decapsulate
from networking_sim.l2_ethernet import frame as eth_frame, unframe as eth_unframe
from networking_sim.l1_physical import to_bits, from_bits
from networking_sim.mock_server import handle_http_request


CLIENT_IP   = "192.0.0.1"
CLIENT_PORT = 50000
CLIENT_MAC  = "aa:bb:cc:dd:ee:ff"

SERVER_PORT = 80
SERVER_MAC  = "11:22:33:44:55:66"

_wire_buffer: bytes = b""

VERBOSE = False

def _dump(label: str, data: bytes, limit: int = 80) -> None:
    if not VERBOSE:
        return
    chunk = data[:limit]
    more = "…" if len(data) > limit else ""
    print(f"  [{label}] {len(data)} B: {chunk!r}{more}")

def _transmit_http(http_bytes: bytes, *, src_ip: str, dst_ip: str,
                   src_mac: str, dst_mac: str, src_port: int, dst_port: int) -> str:
    hs = handshake(src_ip, dst_ip)
    segs = segment(http_bytes, src_port=src_port, dst_port=dst_port, seq0=hs["seq0"])
    _dump("L4 payload", http_bytes)
    print(f"L4: {len(segs)} segment(s), {len(http_bytes)} bytes")

    packets = ip_encapsulate(segs, src_ip=src_ip, dst_ip=dst_ip)
    _dump("L3 first packet", packets[0].payload)
    print(f"L3: {len(packets)} packet(s)")

    frames = eth_frame(packets, src_mac=src_mac, dst_mac=dst_mac)
    print(f"L2: {len(frames)} frame(s)")

    bits = to_bits(frames)
    if VERBOSE:
        print(f"  [L1 bits] {bits[:80]}{'…' if len(bits) > 80 else ''}")

    return bits


def _receive_http(bits: str, *, our_ip: str, our_mac: str) -> bytes:
    frames = from_bits(bits)
    packets = eth_unframe(frames, expected_dst_mac=our_mac)
    segs = ip_decapsulate(packets)
    return reassemble(segs)


def output_request(string: str) -> None:
    global _wire_buffer

    print(f"=== User input ===\n{string}\n")

    # Клиент L7  DNS  L6  L5
    user_request = parse_input(input_str=string)
    print(f"=== L7 parsed ===\n{user_request.model_dump_json(indent=2)}\n")

    host_ip = resolve(host=user_request.host)
    print(f"=== DNS ===\n{user_request.host} -> {host_ip}\n")

    http_bytes = generate_raw_http_request(user_request)
    print(f"=== L7: {len(http_bytes)} bytes of raw HTTP ===\n")

    encoded, ctype = encode(payload=http_bytes)
    encoded = compress(encoded)
    _dump("L6 compressed", encoded)
    print(f"=== L6: {ctype}, {len(encoded)} bytes after compression ===\n")

    session = get_or_create(host=user_request.host, host_ip=host_ip)
    print(f"=== L5: session {session.id} ({session.state}) ===\n")

    # Клиент Сервер
    print(">>> Client → Server")
    bits_to_server = _transmit_http(
        encoded,
        src_ip=CLIENT_IP, dst_ip=host_ip,
        src_mac=CLIENT_MAC, dst_mac=SERVER_MAC,
        src_port=CLIENT_PORT, dst_port=SERVER_PORT,
    )

    # Сервер приём и обработка
    server_received = decompress(
        _receive_http(bits_to_server, our_ip=host_ip, our_mac=SERVER_MAC)
    )
    print(f"=== Server received {len(server_received)} bytes of HTTP ===\n")

    http_response = handle_http_request(server_received)
    print(f"=== Server responded with {len(http_response)} bytes ===\n")

    # Сервер Клиент
    print("<<< Server → Client")
    compressed_response = compress(http_response)
    bits_to_client = _transmit_http(
        compressed_response,
        src_ip=host_ip, dst_ip=CLIENT_IP,
        src_mac=SERVER_MAC, dst_mac=CLIENT_MAC,
        src_port=SERVER_PORT, dst_port=CLIENT_PORT,
    )

    # Клиент приём
    _wire_buffer = _receive_http(bits_to_client, our_ip=CLIENT_IP, our_mac=CLIENT_MAC)
    print(f"=== Client buffered {len(_wire_buffer)} bytes (compressed) ===\n")


def input_response() -> None:
    if not _wire_buffer:
        print("No response yet.")
        return

    raw = decompress(_wire_buffer)
    response: RawHTTPResponse = received_bytes_parse(raw)
    print("=== L7 response ===")
    print(response.model_dump_json(indent=2))


def main() -> None:
    user_req = input("> ")
    output_request(user_req)
    input_response()


def interactive() -> None:
    print("OSI Simulation — вводи HTTP-запрос (например: 'GET example.com/api').")
    print("Команды: 'exit' / 'quit' / Ctrl+C.\n")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nПока.")
            break
        if not line:
            continue
        if line.lower() in ("exit", "quit", "q"):
            break
        try:
            output_request(line)
            input_response()
        except Exception as e:
            print(f"!!! Ошибка: {type(e).__name__}: {e}")
        print()  # пустая строка между запросами


if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if "--verbose" in args or "-v" in args:
        VERBOSE = True
        args = [a for a in args if a not in ("--verbose", "-v")]
    if "--repl" in args:
        interactive()
    else:
        main()