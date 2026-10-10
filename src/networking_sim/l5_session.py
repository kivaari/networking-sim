from .resolve import resolve
from .models import Session, UserRequest
from uuid import uuid4

_sessions: dict[str, Session] = {}

def get_or_create(host: str, host_ip: str) -> Session:
    session_id = uuid4().hex[:8]
    s = _sessions.get(host)
    if s and s.state == "ESTABLISHED": return s
    s = Session(
        id = session_id,
        host=host,
        host_ip = host_ip
    )
    return s

def close(session_id:  str):
    for h, s in _sessions.item():
        if s.id == session_id:
            s.state = "CLOSED"
            del _sessions[h]
            return

def attach(req: UserRequest, sess: Session) -> dict:
    pass