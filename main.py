from networking_sim.l7_http import parse_input
from networking_sim.l6_presentation import encode
from networking_sim.resolve import resolve
from networking_sim.l5_session import get_or_create

def input_response():
    pass

def output_request(string: str):
    print(f"User input: {string}\n")
    user_request = parse_input(input_str=string)
    print(f"Parsed request: {user_request}\n")
    host_ip = resolve(host=user_request.host)
    print(f"IP address: {host_ip}\n")
    encoded_request = encode(payload=user_request.body)
    print(f"Encoded request: {encoded_request}\n")
    session = get_or_create(host=user_request.host, host_ip=host_ip)
    print(f"Session: {session}\n")

def main():
    user_req = input()
    output_request(user_req)

if __name__ == "__main__":
    main()