from pathlib import Path

from fastapi.testclient import TestClient
from pydantic import SecretStr, ValidationError
import pytest

from src.config import Settings
from src.main import create_app
from src.playfab import PlayFabClient, PlayFabError


class FakeTransport:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    async def post(self, url, headers, payload, timeout):
        self.calls.append((url, headers, payload, timeout))
        if self.error:
            raise self.error
        return self.response


def registered_client(tmp_path: Path, *, enabled: bool = False, transport=None):
    settings = Settings(
        database_path=tmp_path / "playfab.db",
        session_ttl_seconds=300,
        playfab_title_id="ABCD1" if enabled else None,
        playfab_secret_key=SecretStr("server-only-secret") if enabled else None,
    )
    app = create_app(settings)
    if enabled:
        app.state.playfab_client = PlayFabClient(
            "ABCD1", "server-only-secret", transport=transport
        )
    client = TestClient(app)
    client.__enter__()
    credentials = {"email": "playfab@example.com", "password": "a secure password"}
    assert client.post("/auth/register", json=credentials).status_code == 201
    token = client.post("/auth/login", json=credentials).json()["access_token"]
    return client, {"Authorization": f"Bearer {token}"}


def test_routes_require_local_authentication(client):
    assert client.get("/integrations/playfab/status").status_code == 401
    assert client.post("/integrations/playfab/link").status_code == 401


def test_disabled_by_default(tmp_path):
    client, headers = registered_client(tmp_path)
    try:
        response = client.get("/integrations/playfab/status", headers=headers)
        assert response.status_code == 200
        assert response.json() == {
            "configured": False,
            "linked": False,
            "playfab_id": None,
            "title_player_account_id": None,
        }
        response = client.post("/integrations/playfab/link", headers=headers)
        assert response.status_code == 503
        assert "secret" not in response.text.casefold()
    finally:
        client.__exit__(None, None, None)


def test_partial_playfab_configuration_fails_closed(tmp_path):
    with pytest.raises(ValidationError):
        Settings(database_path=tmp_path / "partial.db", playfab_title_id="ABCD1")
    with pytest.raises(ValidationError):
        Settings(
            database_path=tmp_path / "partial.db",
            playfab_secret_key=SecretStr("server-only-secret"),
        )


def test_link_uses_stable_opaque_id_and_hides_credentials(tmp_path):
    transport = FakeTransport(
        {"data": {
            "PlayFabId": "PF123",
            "SessionTicket": "raw-session-ticket",
            "EntityToken": {
                "EntityToken": "raw-entity-token",
                "Entity": {"Id": "TPA123", "Type": "title_player_account"},
            },
        }}
    )
    client, headers = registered_client(tmp_path, enabled=True, transport=transport)
    try:
        first = client.post("/integrations/playfab/link", headers=headers)
        second = client.post("/integrations/playfab/link", headers=headers)
        assert first.status_code == second.status_code == 200
        assert first.json() == {
            "configured": True,
            "linked": True,
            "playfab_id": "PF123",
            "title_player_account_id": "TPA123",
        }
        assert "raw-session-ticket" not in first.text
        assert "raw-entity-token" not in first.text
        first_payload, second_payload = transport.calls[0][2], transport.calls[1][2]
        assert first_payload["CustomId"] == second_payload["CustomId"]
        assert first_payload["CustomId"].startswith("dps_")
        assert "@" not in first_payload["CustomId"]
        assert transport.calls[0][0].startswith("https://ABCD1.playfabapi.com/")
        assert transport.calls[0][1]["X-SecretKey"] == "server-only-secret"
        status = client.get("/integrations/playfab/status", headers=headers)
        assert status.json()["linked"] is True
        assert "server-only-secret" not in status.text
    finally:
        client.__exit__(None, None, None)


def test_safe_upstream_error_does_not_leak_credentials(tmp_path):
    transport = FakeTransport(error=PlayFabError("playfab_unavailable", "PlayFab is unavailable"))
    client, headers = registered_client(tmp_path, enabled=True, transport=transport)
    try:
        response = client.post("/integrations/playfab/link", headers=headers)
        assert response.status_code == 502
        assert response.json()["error"]["message"] == "PlayFab is unavailable"
        assert "server-only-secret" not in response.text
        status = client.get("/integrations/playfab/status", headers=headers)
        assert status.json()["linked"] is False
    finally:
        client.__exit__(None, None, None)


def test_malformed_upstream_response_is_normalized(tmp_path):
    transport = FakeTransport({"data": {"SessionTicket": "should-not-leak"}})
    client, headers = registered_client(tmp_path, enabled=True, transport=transport)
    try:
        response = client.post("/integrations/playfab/link", headers=headers)
        assert response.status_code == 502
        assert response.json()["error"]["message"] == "PlayFab returned an invalid response"
        assert "should-not-leak" not in response.text
    finally:
        client.__exit__(None, None, None)


def test_relink_rejects_identity_mismatch(tmp_path):
    transport = FakeTransport({"data": {"PlayFabId": "PF123"}})
    client, headers = registered_client(tmp_path, enabled=True, transport=transport)
    try:
        assert client.post("/integrations/playfab/link", headers=headers).status_code == 200
        transport.response = {"data": {"PlayFabId": "DIFFERENT"}}
        response = client.post("/integrations/playfab/link", headers=headers)
        assert response.status_code == 502
        assert response.json()["error"]["message"] == "PlayFab returned an identity mismatch"
        assert client.get("/integrations/playfab/status", headers=headers).json()["playfab_id"] == "PF123"
    finally:
        client.__exit__(None, None, None)
