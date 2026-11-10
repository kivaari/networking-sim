import pytest
from networking_sim import UserRequest
from networking_sim import l5_session
from networking_sim.l5_session import get_or_create, close, attach


@pytest.fixture(autouse=True)
def clean_sessions():
    l5_session._sessions.clear()
    yield
    l5_session._sessions.clear()


def test_same_host_same_session():
    s1 = get_or_create("example.com", "1.1.1.1")
    s2 = get_or_create("example.com", "1.1.1.1")
    assert s1.id == s2.id
    assert s1.state == "ESTABLISHED"


def test_different_hosts_different_sessions():
    s1 = get_or_create("a.com", "1.1.1.1")
    s2 = get_or_create("b.com", "2.2.2.2")
    assert s1.id != s2.id


def test_close_creates_new():
    s1 = get_or_create("example.com", "1.1.1.1")
    close(s1.id)
    s2 = get_or_create("example.com", "1.1.1.1")
    assert s1.id != s2.id


def test_attach():
    req = UserRequest(method="GET", path="/", host="example.com")
    sess = get_or_create("example.com", "1.1.1.1")
    out = attach(req, sess)
    assert out["session_id"] == sess.id
    assert out["request"] == req
