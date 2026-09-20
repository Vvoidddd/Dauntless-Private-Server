from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


CharacterName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=32)]
ItemCode = Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9_.-]{0,63}$")]


class GameplayModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CharacterCreate(GameplayModel):
    name: CharacterName


class CharacterView(GameplayModel):
    id: int
    name: str
    level: int
    experience: int


class InventoryGrant(GameplayModel):
    item_code: ItemCode
    quantity: int = Field(ge=1, le=999)


class InventoryItemView(GameplayModel):
    item_code: str
    quantity: int


class PartyCreate(GameplayModel):
    character_id: int = Field(gt=0)
    capacity: int = Field(default=4, ge=2, le=4)


class PartyJoin(GameplayModel):
    character_id: int = Field(gt=0)


class PartyView(GameplayModel):
    id: int
    leader_character_id: int
    capacity: int
    status: Literal["open", "queued", "in_hunt", "closed"]
    member_character_ids: list[int]


class MatchmakingRequest(GameplayModel):
    party_id: int = Field(gt=0)


class MatchmakingView(GameplayModel):
    party_id: int
    state: Literal["queued", "matched", "cancelled"]


class HuntResultRequest(GameplayModel):
    result_id: Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9_-]{8,64}$")]
    party_id: int = Field(gt=0)
    character_id: int = Field(gt=0)
    outcome: Literal["completed", "failed"]


class HuntResultView(GameplayModel):
    result_id: str
    applied: bool
    character: CharacterView
