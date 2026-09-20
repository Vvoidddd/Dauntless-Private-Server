from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.config import Settings
from src.main import create_app


@pytest.fixture
def app(tmp_path: Path):
    return create_app(Settings(database_path=tmp_path / "test.db", session_ttl_seconds=300))


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def credentials():
    return {"email": "slayer@example.com", "password": "correct horse battery staple"}


@pytest.fixture
def account(client, credentials):
    response = client.post("/auth/register", json=credentials)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def token(client, credentials, account):
    response = client.post("/auth/login", json=credentials)
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}
