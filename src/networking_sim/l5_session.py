from .models import Session, UserRequest
from uuid import uuid4

_sessions: dict[str, Session] = {}

def get_or_create(host: str, host_ip: str) -> Session:
    s = _sessions.get(host)
    if s and s.state == "ESTABLISHED": return s
    session_id = uuid4().hex[:8]
    s = Session(
        id = session_id,
        host=host,
        host_ip = host_ip
    )
    _sessions[host] = s
    return s

def close(session_id:  str):
    for h, s in _sessions.items():
        if s.id == session_id:
            s.state = "CLOSED"
            _sessions.pop(h)
            return

def attach(req: UserRequest, sess: Session) -> dict:
    return {"session_id": sess.id, "request":req}