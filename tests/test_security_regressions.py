import pytest
from pydantic import ValidationError

from src.config import Settings
from src.gameplay.schemas import CharacterCreate, HuntResultRequest, PartyCreate
from src.security import hash_token, verify_password


def test_debug_mode_cannot_bind_to_non_loopback(tmp_path):
    with pytest.raises(ValidationError):
        Settings(debug=True, host="0.0.0.0", database_path=tmp_path / "db.sqlite")


def test_gameplay_requests_reject_mass_assignment_fields():
    cases = [
        (CharacterCreate, {"name": "Alpha One", "account_id": "victim"}),
        (PartyCreate, {"character_id": 1, "capacity": 4, "status": "in_hunt"}),
        (
            HuntResultRequest,
            {
                "result_id": "result_001",
                "party_id": 1,
                "character_id": 1,
                "outcome": "completed",
                "experience": 999999,
            },
        ),
    ]
    for schema, body in cases:
        with pytest.raises(ValidationError):
            schema.model_validate(body)


def test_token_hashing_handles_untrusted_unicode_without_leaking_token():
    token = "invalid-\N{SNOWMAN}-bearer"
    digest = hash_token(token)
    assert token not in digest
    assert len(digest) == 64


def test_password_verification_rejects_untrusted_work_factors():
    malicious = "scrypt$1073741824$8$1$" + "QQ==" + "$" + "QQ=="
    assert verify_password("password", malicious) is False


def test_sessions_store_only_token_digest(client, app, credentials, account):
    token = client.post("/auth/login", json=credentials).json()["access_token"]
    with app.state.db.connect() as connection:
        row = connection.execute("SELECT token_hash FROM sessions").fetchone()
    assert row["token_hash"] == hash_token(token)
    assert token not in row["token_hash"]


def test_sql_metacharacters_do_not_bypass_auth(client, credentials, account):
    response = client.post(
        "/auth/login",
        json={"email": "' OR 1=1 --@example.test", "password": credentials["password"]},
    )
    assert response.status_code == 401
