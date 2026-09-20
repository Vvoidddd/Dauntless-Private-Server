from collections.abc import Callable

from fastapi import APIRouter, Depends, HTTPException, Response, status

from .schemas import (
    CharacterCreate, CharacterView, HuntResultRequest, HuntResultView,
    InventoryItemView, MatchmakingRequest, MatchmakingView, PartyCreate,
    PartyJoin, PartyView,
)
from .service import GameplayError, GameplayService


def build_gameplay_router(
    service: GameplayService,
    current_account_id: Callable[..., str],
) -> APIRouter:
    router = APIRouter(prefix="/api", tags=["gameplay"])

    def call(method, *args):
        try:
            return method(*args)
        except GameplayError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

    @router.post("/characters", response_model=CharacterView, status_code=status.HTTP_201_CREATED)
    def create_character(body: CharacterCreate, account_id: str = Depends(current_account_id)):
        return call(service.create_character, account_id, body.name)

    @router.get("/characters", response_model=list[CharacterView])
    def list_characters(account_id: str = Depends(current_account_id)):
        return service.list_characters(account_id)

    @router.get("/characters/{character_id}/inventory", response_model=list[InventoryItemView])
    def inventory(character_id: int, account_id: str = Depends(current_account_id)):
        return call(service.inventory, account_id, character_id)

    @router.post("/parties", response_model=PartyView, status_code=status.HTTP_201_CREATED)
    def create_party(body: PartyCreate, account_id: str = Depends(current_account_id)):
        return call(service.create_party, account_id, body.character_id, body.capacity)

    @router.get("/parties/{party_id}", response_model=PartyView)
    def get_party(party_id: int, account_id: str = Depends(current_account_id)):
        return call(service.get_party, account_id, party_id)

    @router.post("/parties/{party_id}/members", response_model=PartyView)
    def join_party(party_id: int, body: PartyJoin, account_id: str = Depends(current_account_id)):
        return call(service.join_party, account_id, party_id, body.character_id)

    @router.delete("/parties/{party_id}/members/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
    def leave_party(party_id: int, character_id: int, account_id: str = Depends(current_account_id)):
        call(service.leave_party, account_id, party_id, character_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @router.post("/matchmaking", response_model=MatchmakingView)
    def queue(body: MatchmakingRequest, account_id: str = Depends(current_account_id)):
        return call(service.queue_party, account_id, body.party_id)

    @router.delete("/matchmaking/{party_id}", response_model=MatchmakingView)
    def cancel_queue(party_id: int, account_id: str = Depends(current_account_id)):
        return call(service.cancel_queue, account_id, party_id)

    @router.post("/simulated-hunts/results", response_model=HuntResultView)
    def hunt_result(body: HuntResultRequest, account_id: str = Depends(current_account_id)):
        return call(service.apply_hunt_result, account_id, body.model_dump(mode="json"))

    return router
