"""Local account and opaque bearer-session API."""
import sqlite3
from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.db import Database
from src.models import AccountResponse, LoginRequest, RegisterRequest, TokenResponse, ValidationResponse
from src.security import hash_password, hash_token, new_session_token, verify_password

router = APIRouter(prefix="/auth", tags=["authentication"])
bearer = HTTPBearer(auto_error=False)
# Ensures unknown-account logins still perform the password KDF, reducing the
# usefulness of timing measurements for account discovery.
DUMMY_PASSWORD_HASH = hash_password("not-a-real-account-password")

def utcnow() -> datetime: return datetime.now(UTC)
def get_database(request: Request) -> Database: return request.app.state.db
def unauthorized() -> HTTPException:
    return HTTPException(status_code=401, detail="Invalid or expired credentials")

def current_session(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    db: Annotated[Database, Depends(get_database)],
):
    if credentials is None or credentials.scheme.casefold() != "bearer": raise unauthorized()
    with db.connect() as connection:
        row = connection.execute(
            """SELECT a.id, a.email, a.created_at, s.id AS session_id, s.expires_at
            FROM sessions s JOIN accounts a ON a.id=s.account_id
            WHERE s.token_hash=? AND s.revoked_at IS NULL AND s.expires_at>?""",
            (hash_token(credentials.credentials), utcnow().isoformat()),
        ).fetchone()
    if row is None: raise unauthorized()
    return row

def current_account_id(session=Depends(current_session)) -> str:
    return session["id"]

def issue_token(connection: sqlite3.Connection, account_id: str, ttl: int) -> TokenResponse:
    token, created = new_session_token(), utcnow()
    expires = created + timedelta(seconds=ttl)
    connection.execute(
        "INSERT INTO sessions(id,account_id,token_hash,created_at,expires_at) VALUES(?,?,?,?,?)",
        (str(uuid4()), account_id, hash_token(token), created.isoformat(), expires.isoformat()),
    )
    return TokenResponse(access_token=token, expires_at=expires)

@router.post("/register", response_model=AccountResponse, status_code=201)
def register(payload: RegisterRequest, db: Annotated[Database, Depends(get_database)]):
    account_id, created = str(uuid4()), utcnow()
    try:
        with db.connect() as connection:
            connection.execute(
                "INSERT INTO accounts(id,email,password_hash,created_at,updated_at) VALUES(?,?,?,?,?)",
                (account_id, payload.email, hash_password(payload.password), created.isoformat(), created.isoformat()),
            )
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="An account with this email already exists") from exc
    return AccountResponse(id=account_id, email=payload.email, created_at=created)

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Annotated[Database, Depends(get_database)]):
    with db.connect() as connection:
        account = connection.execute("SELECT id,password_hash FROM accounts WHERE email=?", (payload.email,)).fetchone()
        candidate_hash = account["password_hash"] if account is not None else DUMMY_PASSWORD_HASH
        password_valid = verify_password(payload.password, candidate_hash)
        if account is None or not password_valid: raise unauthorized()
        return issue_token(connection, account["id"], request.app.state.settings.session_ttl_seconds)

@router.post("/validate-token", response_model=ValidationResponse)
def validate_token(session=Depends(current_session)):
    account = AccountResponse(id=session["id"], email=session["email"], created_at=session["created_at"])
    return ValidationResponse(account=account, expires_at=session["expires_at"])

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(session=Depends(current_session), db: Database = Depends(get_database)) -> None:
    with db.connect() as connection:
        connection.execute("UPDATE sessions SET revoked_at=? WHERE id=?", (utcnow().isoformat(), session["session_id"]))

@router.get("/profile/me", response_model=AccountResponse)
def profile_me(session=Depends(current_session)):
    return AccountResponse(id=session["id"], email=session["email"], created_at=session["created_at"])
