import pytest
from networking_sim import resolve as resolve_mod
from networking_sim.resolve import resolve


@pytest.fixture(autouse=True)
def clean_cache():
    resolve_mod.CACHE.clear()
    yield
    resolve_mod.CACHE.clear()


def test_known_host():
    assert resolve("example.com") == "162.21.12.12"


def test_case_insensitive():
    assert resolve("Example.COM") == "162.21.12.12"


def test_unknown_host():
    with pytest.raises(ValueError, match="NXDOMAIN"):
        resolve("no-such-host.invalid")


def test_cache():
    resolve("example.com")
    assert "example.com" in resolve_mod.CACHE
