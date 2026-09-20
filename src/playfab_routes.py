"""Authenticated routes for the optional PlayFab identity link."""
import sqlite3
from datetime import UTC, datetime
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from src.auth import current_account_id, get_database
from src.db import Database
from src.playfab import PlayFabClient, PlayFabError

router = APIRouter(prefix="/integrations/playfab", tags=["integrations"])


class PlayFabStatus(BaseModel):
    configured: bool
    linked: bool
    playfab_id: str | None = None
    title_player_account_id: str | None = None


def get_client(request: Request) -> PlayFabClient:
    return request.app.state.playfab_client


def _read_link(db: Database, account_id: str):
    with db.connect() as connection:
        return connection.execute(
            "SELECT custom_id,playfab_id,title_player_account_id FROM playfab_links WHERE account_id=?",
            (account_id,),
        ).fetchone()


def _get_or_create_custom_id(db: Database, account_id: str) -> str:
    row = _read_link(db, account_id)
    if row is not None:
        return row["custom_id"]
    now, custom_id = datetime.now(UTC).isoformat(), f"dps_{uuid4().hex}"
    try:
        with db.connect() as connection:
            connection.execute(
                "INSERT INTO playfab_links(account_id,custom_id,created_at,updated_at) VALUES(?,?,?,?)",
                (account_id, custom_id, now, now),
            )
    except sqlite3.IntegrityError:
        # A concurrent request won the insert; preserve its stable identifier.
        row = _read_link(db, account_id)
        if row is None:
            raise
        return row["custom_id"]
    return custom_id


@router.get("/status", response_model=PlayFabStatus)
def status(
    account_id: Annotated[str, Depends(current_account_id)],
    db: Annotated[Database, Depends(get_database)],
    client: Annotated[PlayFabClient, Depends(get_client)],
):
    row = _read_link(db, account_id)
    linked = row is not None and row["playfab_id"] is not None
    return PlayFabStatus(
        configured=client.enabled,
        linked=linked,
        playfab_id=row["playfab_id"] if linked else None,
        title_player_account_id=row["title_player_account_id"] if linked else None,
    )


@router.post("/link", response_model=PlayFabStatus)
async def link(
    account_id: Annotated[str, Depends(current_account_id)],
    db: Annotated[Database, Depends(get_database)],
    client: Annotated[PlayFabClient, Depends(get_client)],
):
    if not client.enabled:
        raise HTTPException(status_code=503, detail="PlayFab integration is not configured")
    custom_id = _get_or_create_custom_id(db, account_id)
    try:
        identity = await client.login_with_custom_id(custom_id)
    except PlayFabError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    existing = _read_link(db, account_id)
    if existing is not None and existing["playfab_id"] not in {None, identity.playfab_id}:
        raise HTTPException(status_code=502, detail="PlayFab returned an identity mismatch")
    now = datetime.now(UTC).isoformat()
    with db.connect() as connection:
        connection.execute(
            """UPDATE playfab_links SET playfab_id=?,title_player_account_id=?,updated_at=?
            WHERE account_id=?""",
            (identity.playfab_id, identity.title_player_account_id, now, account_id),
        )
    return PlayFabStatus(
        configured=True,
        linked=True,
        playfab_id=identity.playfab_id,
        title_player_account_id=identity.title_player_account_id,
    )
