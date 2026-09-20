"""Clean-room gameplay-domain HTTP API."""

from .routes import build_gameplay_router
from .service import GameplayService

__all__ = ["GameplayService", "build_gameplay_router"]
