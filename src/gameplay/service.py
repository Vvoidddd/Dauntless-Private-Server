import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class GameplayError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class GameplayService:
    """Transactional gameplay persistence independent of any proprietary client."""

    def __init__(self, database_path: str | Path):
        self.database_path = str(database_path)

    @contextmanager
    def connection(self, *, write: bool = False) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            if write:
                connection.execute("BEGIN IMMEDIATE")
            yield connection
            if write:
                connection.commit()
        except Exception:
            if write:
                connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        with self.connection(write=True) as db:
            db.executescript(SCHEMA)

    @staticmethod
    def _owned_character(db: sqlite3.Connection, account_id: str, character_id: int) -> sqlite3.Row:
        row = db.execute(
            "SELECT id, name, level, experience FROM gameplay_characters WHERE id=? AND account_id=?",
            (character_id, account_id),
        ).fetchone()
        if row is None:
            # Do not reveal whether another account owns the identifier.
            raise GameplayError(404, "character not found")
        return row

    def create_character(self, account_id: str, name: str) -> dict:
        with self.connection(write=True) as db:
            try:
                cursor = db.execute(
                    "INSERT INTO gameplay_characters(account_id, name) VALUES (?, ?)",
                    (account_id, name),
                )
            except sqlite3.IntegrityError as exc:
                raise GameplayError(409, "character name is unavailable") from exc
            return dict(self._owned_character(db, account_id, cursor.lastrowid))

    def list_characters(self, account_id: str) -> list[dict]:
        with self.connection() as db:
            return [dict(row) for row in db.execute(
                "SELECT id, name, level, experience FROM gameplay_characters WHERE account_id=? ORDER BY id",
                (account_id,),
            )]

    def inventory(self, account_id: str, character_id: int) -> list[dict]:
        with self.connection() as db:
            self._owned_character(db, account_id, character_id)
            return [dict(row) for row in db.execute(
                "SELECT item_code, quantity FROM gameplay_inventory WHERE character_id=? ORDER BY item_code",
                (character_id,),
            )]

    def _party(self, db: sqlite3.Connection, party_id: int) -> dict:
        party = db.execute("SELECT * FROM gameplay_parties WHERE id=?", (party_id,)).fetchone()
        if party is None:
            raise GameplayError(404, "party not found")
        result = dict(party)
        result["member_character_ids"] = [row[0] for row in db.execute(
            "SELECT character_id FROM gameplay_party_members WHERE party_id=? ORDER BY joined_at, character_id",
            (party_id,),
        )]
        return result

    def _owned_party_member(self, db: sqlite3.Connection, account_id: str, party_id: int, character_id: int) -> None:
        self._owned_character(db, account_id, character_id)
        if db.execute(
            "SELECT 1 FROM gameplay_party_members WHERE party_id=? AND character_id=?",
            (party_id, character_id),
        ).fetchone() is None:
            raise GameplayError(404, "party membership not found")

    def create_party(self, account_id: str, character_id: int, capacity: int) -> dict:
        with self.connection(write=True) as db:
            self._owned_character(db, account_id, character_id)
            if db.execute("SELECT 1 FROM gameplay_party_members WHERE character_id=?", (character_id,)).fetchone():
                raise GameplayError(409, "character is already in a party")
            cursor = db.execute(
                "INSERT INTO gameplay_parties(leader_character_id, capacity) VALUES (?, ?)",
                (character_id, capacity),
            )
            db.execute(
                "INSERT INTO gameplay_party_members(party_id, character_id) VALUES (?, ?)",
                (cursor.lastrowid, character_id),
            )
            return self._party(db, cursor.lastrowid)

    def get_party(self, account_id: str, party_id: int) -> dict:
        with self.connection() as db:
            party = self._party(db, party_id)
            placeholders = ",".join("?" for _ in party["member_character_ids"])
            owned = db.execute(
                f"SELECT 1 FROM gameplay_characters WHERE account_id=? AND id IN ({placeholders})",
                (account_id, *party["member_character_ids"]),
            ).fetchone()
            if owned is None:
                raise GameplayError(404, "party not found")
            return party

    def join_party(self, account_id: str, party_id: int, character_id: int) -> dict:
        with self.connection(write=True) as db:
            self._owned_character(db, account_id, character_id)
            party = self._party(db, party_id)
            if party["status"] != "open":
                raise GameplayError(409, "party is not open")
            if len(party["member_character_ids"]) >= party["capacity"]:
                raise GameplayError(409, "party is full")
            try:
                db.execute(
                    "INSERT INTO gameplay_party_members(party_id, character_id) VALUES (?, ?)",
                    (party_id, character_id),
                )
            except sqlite3.IntegrityError as exc:
                raise GameplayError(409, "character is already in a party") from exc
            return self._party(db, party_id)

    def leave_party(self, account_id: str, party_id: int, character_id: int) -> None:
        with self.connection(write=True) as db:
            self._owned_party_member(db, account_id, party_id, character_id)
            party = self._party(db, party_id)
            if party["status"] != "open":
                raise GameplayError(409, "cannot leave party in its current state")
            if party["leader_character_id"] == character_id and len(party["member_character_ids"]) > 1:
                raise GameplayError(409, "leader must remove members or close the party")
            db.execute("DELETE FROM gameplay_party_members WHERE party_id=? AND character_id=?", (party_id, character_id))
            if party["leader_character_id"] == character_id:
                db.execute("UPDATE gameplay_parties SET status='closed' WHERE id=?", (party_id,))

    def queue_party(self, account_id: str, party_id: int) -> dict:
        with self.connection(write=True) as db:
            party = self._party(db, party_id)
            self._owned_character(db, account_id, party["leader_character_id"])
            if party["status"] != "open":
                raise GameplayError(409, "party cannot enter matchmaking")
            db.execute("UPDATE gameplay_parties SET status='queued' WHERE id=?", (party_id,))
            db.execute(
                "INSERT INTO gameplay_matchmaking(party_id, state) VALUES (?, 'queued') "
                "ON CONFLICT(party_id) DO UPDATE SET state='queued', updated_at=CURRENT_TIMESTAMP",
                (party_id,),
            )
            return {"party_id": party_id, "state": "queued"}

    def cancel_queue(self, account_id: str, party_id: int) -> dict:
        with self.connection(write=True) as db:
            party = self._party(db, party_id)
            self._owned_character(db, account_id, party["leader_character_id"])
            if party["status"] != "queued":
                raise GameplayError(409, "party is not queued")
            db.execute("UPDATE gameplay_parties SET status='open' WHERE id=?", (party_id,))
            db.execute("UPDATE gameplay_matchmaking SET state='cancelled', updated_at=CURRENT_TIMESTAMP WHERE party_id=?", (party_id,))
            return {"party_id": party_id, "state": "cancelled"}

    def apply_hunt_result(self, account_id: str, payload: dict) -> dict:
        with self.connection(write=True) as db:
            character = self._owned_character(db, account_id, payload["character_id"])
            self._owned_party_member(db, account_id, payload["party_id"], payload["character_id"])
            party = self._party(db, payload["party_id"])
            if party["leader_character_id"] != payload["character_id"]:
                raise GameplayError(403, "only the party leader may submit a simulated result")
            existing = db.execute("SELECT payload FROM gameplay_hunt_results WHERE result_id=?", (payload["result_id"],)).fetchone()
            canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
            if existing:
                if existing["payload"] != canonical:
                    raise GameplayError(409, "result id was already used with different data")
                return {"result_id": payload["result_id"], "applied": False, "character": dict(character)}
            if party["status"] not in ("queued", "in_hunt"):
                raise GameplayError(409, "party has no active simulated hunt")
            db.execute("UPDATE gameplay_parties SET status='open' WHERE id=?", (payload["party_id"],))
            db.execute("UPDATE gameplay_matchmaking SET state='matched', updated_at=CURRENT_TIMESTAMP WHERE party_id=?", (payload["party_id"],))
            if payload["outcome"] == "completed":
                # Simulation rewards are server-defined; callers cannot mint arbitrary items.
                experience = 100
                db.execute(
                    "UPDATE gameplay_characters SET experience=experience+? WHERE id=?",
                    (experience, payload["character_id"]),
                )
                db.execute(
                    "INSERT INTO gameplay_inventory(character_id,item_code,quantity) VALUES (?, 'training-token', 1) "
                    "ON CONFLICT(character_id,item_code) DO UPDATE SET quantity=quantity+1",
                    (payload["character_id"],),
                )
            db.execute(
                "INSERT INTO gameplay_hunt_results(result_id, party_id, character_id, payload) VALUES (?,?,?,?)",
                (payload["result_id"], payload["party_id"], payload["character_id"], canonical),
            )
            updated = self._owned_character(db, account_id, payload["character_id"])
            return {"result_id": payload["result_id"], "applied": True, "character": dict(updated)}


SCHEMA = """
CREATE TABLE IF NOT EXISTS gameplay_characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    name TEXT NOT NULL COLLATE NOCASE UNIQUE,
    level INTEGER NOT NULL DEFAULT 1 CHECK(level >= 1),
    experience INTEGER NOT NULL DEFAULT 0 CHECK(experience >= 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_gameplay_characters_account ON gameplay_characters(account_id);
CREATE TABLE IF NOT EXISTS gameplay_inventory (
    character_id INTEGER NOT NULL REFERENCES gameplay_characters(id) ON DELETE CASCADE,
    item_code TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity BETWEEN 0 AND 999999),
    PRIMARY KEY(character_id, item_code)
);
CREATE TABLE IF NOT EXISTS gameplay_parties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    leader_character_id INTEGER NOT NULL REFERENCES gameplay_characters(id),
    capacity INTEGER NOT NULL CHECK(capacity BETWEEN 2 AND 4),
    status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open','queued','in_hunt','closed')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS gameplay_party_members (
    party_id INTEGER NOT NULL REFERENCES gameplay_parties(id) ON DELETE CASCADE,
    character_id INTEGER NOT NULL UNIQUE REFERENCES gameplay_characters(id) ON DELETE CASCADE,
    joined_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(party_id, character_id)
);
CREATE TABLE IF NOT EXISTS gameplay_matchmaking (
    party_id INTEGER PRIMARY KEY REFERENCES gameplay_parties(id) ON DELETE CASCADE,
    state TEXT NOT NULL CHECK(state IN ('queued','matched','cancelled')),
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS gameplay_hunt_results (
    result_id TEXT PRIMARY KEY,
    party_id INTEGER NOT NULL REFERENCES gameplay_parties(id),
    character_id INTEGER NOT NULL REFERENCES gameplay_characters(id),
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""
