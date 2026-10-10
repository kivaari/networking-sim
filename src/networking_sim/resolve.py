DNS_TABLE = {"example.com": "162.21.12.12", "api.example.com": "192.32.34.45", "api.test.com": "192.23.54.76", "localhost": "192.0.0.1"}
CACHE = {}

def resolve(host: str) -> str: #DNS Resolver like thing
    host = host.lower()
    if host in CACHE: return CACHE[host]
    if host not in DNS_TABLE: raise ValueError(f"NXDOMAIN: {host}")
    CACHE[host] = DNS_TABLE[host]
    return CACHE[host]