from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class UserRequest(BaseModel):
    method: str = Field(..., pattern="^(GET|POST|PUT|PATCH|DELETE)$")
    path: str
    protocol_version: str = "HTTP/1.1"
    host: str
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    accept: str = "*/*"
    content_type: Optional[str] = None
    body: Optional[Any] = None

class RawHTTPResponse(BaseModel):
    protocol_version: str = Field(..., pattern="^(HTTP/1.1|HTTP/2)")
    status: str
    content_type: Optional[str] = None
    content_length: Optional[str] = None
    connection: Optional[str] = None
    server: Optional[str] = None
    date: Optional[str] = None
    body: Optional[Any] = None

class Session(BaseModel):
    id: str
    host: Optional[str] = None
    host_ip: Optional[str] = None
    state: str = "ESTABLISHED"

class Segment(BaseModel):
    model_config = ConfigDict(ser_json_bytes='base64', val_json_bytes='base64')
    src_port: int
    dst_port: int
    seq: int
    ack: int
    flags: set[str]
    payload: Optional[bytes] = None
    checksum: int

class Packet(BaseModel):
    model_config = ConfigDict(ser_json_bytes='base64', val_json_bytes='base64')
    src_ip: str
    dst_ip: str
    ttl: int = 64
    protocol: str = "TCP"
    payload: bytes
    header_checksum: int

class Frame(BaseModel):
    model_config = ConfigDict(ser_json_bytes='base64', val_json_bytes='base64')
    src_mac: str
    dst_mac: str
    ethertype: int = 0x0800
    payload: bytes
    fcs: int