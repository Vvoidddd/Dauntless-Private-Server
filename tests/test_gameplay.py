from datetime import datetime, timezone

import pytest

from src.db import Database
from src.gameplay.service import GameplayError, GameplayService


@pytest.fixture()
def gameplay(tmp_path):
    path = tmp_path / "gameplay.sqlite"
    database = Database(path)
    database.initialize()
    now = datetime.now(timezone.utc).isoformat()
    with database.connect() as connection:
        connection.executemany(
            "INSERT INTO accounts(id,email,password_hash,created_at,updated_at) VALUES(?,?,?,?,?)",
            [
                ("account-a", "a@example.test", "unused", now, now),
                ("account-b", "b@example.test", "unused", now, now),
                ("account-c", "c@example.test", "unused", now, now),
            ],
        )
    service = GameplayService(path)
    service.initialize()
    return service


def assert_gameplay_error(status_code, operation):
    with pytest.raises(GameplayError) as caught:
        operation()
    assert caught.value.status_code == status_code


def test_character_listing_and_inventory_enforce_ownership(gameplay):
    alpha = gameplay.create_character("account-a", "Alpha One")
    beta = gameplay.create_character("account-b", "Beta Two")

    assert gameplay.list_characters("account-a") == [alpha]
    assert gameplay.list_characters("account-b") == [beta]
    assert gameplay.inventory("account-a", alpha["id"]) == []
    assert_gameplay_error(404, lambda: gameplay.inventory("account-b", alpha["id"]))


def test_character_names_are_unique_case_insensitively(gameplay):
    gameplay.create_character("account-a", "Alpha One")
    assert_gameplay_error(
        409, lambda: gameplay.create_character("account-b", "alpha one")
    )


def test_party_capacity_join_and_leave_constraints(gameplay):
    leader = gameplay.create_character("account-a", "Alpha One")
    member = gameplay.create_character("account-b", "Beta Two")
    extra = gameplay.create_character("account-c", "Gamma Three")
    party = gameplay.create_party("account-a", leader["id"], 2)

    joined = gameplay.join_party("account-b", party["id"], member["id"])
    assert joined["member_character_ids"] == [leader["id"], member["id"]]
    assert_gameplay_error(
        409,
        lambda: gameplay.join_party("account-c", party["id"], extra["id"]),
    )
    assert_gameplay_error(
        409,
        lambda: gameplay.leave_party("account-a", party["id"], leader["id"]),
    )

    gameplay.leave_party("account-b", party["id"], member["id"])
    assert gameplay.get_party("account-a", party["id"])["member_character_ids"] == [
        leader["id"]
    ]
    assert_gameplay_error(
        404,
        lambda: gameplay.leave_party("account-a", party["id"], member["id"]),
    )


def test_only_leader_can_control_matchmaking_and_states_are_guarded(gameplay):
    leader = gameplay.create_character("account-a", "Alpha One")
    member = gameplay.create_character("account-b", "Beta Two")
    party = gameplay.create_party("account-a", leader["id"], 4)
    gameplay.join_party("account-b", party["id"], member["id"])

    assert_gameplay_error(404, lambda: gameplay.queue_party("account-b", party["id"]))
    assert gameplay.queue_party("account-a", party["id"])["state"] == "queued"
    assert gameplay.get_party("account-a", party["id"])["status"] == "queued"
    assert_gameplay_error(409, lambda: gameplay.queue_party("account-a", party["id"]))
    assert_gameplay_error(
        409,
        lambda: gameplay.leave_party("account-b", party["id"], member["id"]),
    )
    assert_gameplay_error(404, lambda: gameplay.cancel_queue("account-b", party["id"]))

    assert gameplay.cancel_queue("account-a", party["id"])["state"] == "cancelled"
    assert gameplay.get_party("account-a", party["id"])["status"] == "open"
    assert_gameplay_error(409, lambda: gameplay.cancel_queue("account-a", party["id"]))


def test_hunt_rewards_are_idempotent_and_populate_inventory(gameplay):
    leader = gameplay.create_character("account-a", "Alpha One")
    party = gameplay.create_party("account-a", leader["id"], 4)
    gameplay.queue_party("account-a", party["id"])
    result = {
        "result_id": "result_001",
        "party_id": party["id"],
        "character_id": leader["id"],
        "outcome": "completed",
    }

    first = gameplay.apply_hunt_result("account-a", result)
    replay = gameplay.apply_hunt_result("account-a", result)

    assert first["applied"] is True
    assert first["character"]["experience"] == 100
    assert replay["applied"] is False
    assert replay["character"]["experience"] == 100
    assert gameplay.inventory("account-a", leader["id"]) == [
        {"item_code": "training-token", "quantity": 1}
    ]
    assert gameplay.get_party("account-a", party["id"])["status"] == "open"


def test_hunt_result_replay_conflict_does_not_apply_second_reward(gameplay):
    leader = gameplay.create_character("account-a", "Alpha One")
    party = gameplay.create_party("account-a", leader["id"], 4)
    gameplay.queue_party("account-a", party["id"])
    original = {
        "result_id": "result_001",
        "party_id": party["id"],
        "character_id": leader["id"],
        "outcome": "completed",
    }
    gameplay.apply_hunt_result("account-a", original)

    changed = {**original, "outcome": "failed"}
    assert_gameplay_error(
        409, lambda: gameplay.apply_hunt_result("account-a", changed)
    )
    assert gameplay.list_characters("account-a")[0]["experience"] == 100
    assert gameplay.inventory("account-a", leader["id"])[0]["quantity"] == 1


def test_nonleader_cannot_submit_hunt_rewards(gameplay):
    leader = gameplay.create_character("account-a", "Alpha One")
    member = gameplay.create_character("account-b", "Beta Two")
    party = gameplay.create_party("account-a", leader["id"], 4)
    gameplay.join_party("account-b", party["id"], member["id"])
    gameplay.queue_party("account-a", party["id"])

    assert_gameplay_error(
        403,
        lambda: gameplay.apply_hunt_result(
            "account-b",
            {
                "result_id": "result_002",
                "party_id": party["id"],
                "character_id": member["id"],
                "outcome": "completed",
            },
        ),
    )
    assert gameplay.inventory("account-b", member["id"]) == []
