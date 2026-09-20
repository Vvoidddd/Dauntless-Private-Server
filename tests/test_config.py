from pathlib import Path

import pytest
from pydantic import ValidationError

from src.config import Settings


def test_defaults_are_safe_and_local(monkeypatch):
    monkeypatch.delenv("DPS_HOST", raising=False)
    monkeypatch.delenv("DPS_DATABASE_PATH", raising=False)
    settings = Settings(_env_file=None)
    assert settings.host == "127.0.0.1"
    assert settings.database_path == Path("data/server.db")


def test_only_dps_prefixed_environment_is_used(monkeypatch):
    monkeypatch.setenv("PORT", "9999")
    monkeypatch.setenv("DPS_PORT", "8123")
    assert Settings(_env_file=None).port == 8123


@pytest.mark.parametrize("port", [0, 65536])
def test_invalid_port_is_rejected(port):
    with pytest.raises(ValidationError):
        Settings(port=port, _env_file=None)


def test_invalid_session_ttl_is_rejected():
    with pytest.raises(ValidationError):
        Settings(session_ttl_seconds=299, _env_file=None)
