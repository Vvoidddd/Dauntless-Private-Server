from datetime import UTC, datetime, timedelta


def test_registration_normalizes_email(client, credentials):
    credentials["email"] = "  Slayer@Example.COM  "
    response = client.post("/auth/register", json=credentials)
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "slayer@example.com"
    assert body["id"]
    assert "password" not in body


def test_duplicate_email_conflicts_case_insensitively(client, credentials, account):
    credentials["email"] = credentials["email"].upper()
    response = client.post("/auth/register", json=credentials)
    assert response.status_code == 409
    assert response.json()["error"]["message"] == "An account with this email already exists"


def test_register_validation_is_uniform(client):
    response = client.post("/auth/register", json={"email": "bad", "password": "short", "extra": True})
    assert response.status_code == 422
    body = response.json()["error"]
    assert body["code"] == "validation_error"
    assert body["details"]


def test_login_validate_and_profile(client, credentials, account):
    response = client.post("/auth/login", json=credentials)
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert response.json()["token_type"] == "bearer"
    headers = {"Authorization": f"Bearer {token}"}
    validation = client.post("/auth/validate-token", headers=headers)
    assert validation.status_code == 200
    assert validation.json()["valid"] is True
    assert validation.json()["account"]["id"] == account["id"]
    profile = client.get("/auth/profile/me", headers=headers)
    assert profile.status_code == 200
    assert profile.json() == account


def test_wrong_and_unknown_credentials_are_indistinguishable(client, credentials, account):
    wrong = client.post("/auth/login", json={**credentials, "password": "this password is wrong"})
    unknown = client.post("/auth/login", json={**credentials, "email": "unknown@example.com"})
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()


def test_missing_and_invalid_bearer_are_rejected(client):
    missing = client.get("/auth/profile/me")
    invalid = client.get("/auth/profile/me", headers={"Authorization": "Bearer invalid"})
    assert missing.status_code == invalid.status_code == 401


def test_logout_revokes_only_presented_session(client, credentials, account):
    first = client.post("/auth/login", json=credentials).json()["access_token"]
    second = client.post("/auth/login", json=credentials).json()["access_token"]
    assert client.post("/auth/logout", headers={"Authorization": f"Bearer {first}"}).status_code == 204
    assert client.post("/auth/validate-token", headers={"Authorization": f"Bearer {first}"}).status_code == 401
    assert client.post("/auth/validate-token", headers={"Authorization": f"Bearer {second}"}).status_code == 200


def test_expired_session_is_rejected(client, app, token):
    expired = (datetime.now(UTC) - timedelta(seconds=1)).isoformat()
    with app.state.db.connect() as connection:
        connection.execute("UPDATE sessions SET expires_at=?", (expired,))
    response = client.post("/auth/validate-token", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
