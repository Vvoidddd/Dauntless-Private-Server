"""FastAPI application entry point."""
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Support IDEs that execute this file directly (``python src/main.py``).
# Package execution (``python -m src.main``) already includes the project root.
if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.auth import current_account_id, router as auth_router
from src.config import Settings, get_settings
from src.db import Database
from src.playfab import PlayFabClient
from src.playfab_routes import router as playfab_router

def error_response(status_code: int, code: str, message: str, details=None) -> JSONResponse:
    error = {"code": code, "message": message}
    if details is not None: error["details"] = details
    return JSONResponse(status_code=status_code, content={"error": error})

def create_app(settings: Settings | None = None) -> FastAPI:
    configured = settings or get_settings()
    db = Database(configured.database_path)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        db.initialize()
        gameplay_service = getattr(app.state, "gameplay_service", None)
        if gameplay_service is not None: gameplay_service.initialize()
        yield

    app = FastAPI(title=configured.app_name, debug=configured.debug, lifespan=lifespan)
    app.state.settings, app.state.db = configured, db
    app.state.playfab_client = PlayFabClient.from_settings(configured)
    app.include_router(auth_router)
    app.include_router(playfab_router)

    # Gameplay is optional so the auth foundation remains independently usable.
    try:
        from src.gameplay.routes import build_gameplay_router
        from src.gameplay.service import GameplayService
        app.state.gameplay_service = GameplayService(configured.database_path)
        app.include_router(build_gameplay_router(app.state.gameplay_service, current_account_id))
    except ImportError:
        pass

    @app.exception_handler(StarletteHTTPException)
    async def http_error(_: Request, exc: StarletteHTTPException):
        return error_response(exc.status_code, "request_error", str(exc.detail))

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, exc: RequestValidationError):
        # Pydantic may include a non-JSON-serializable ValueError under ``ctx``.
        details = [{key: value for key, value in item.items() if key != "ctx"} for item in exc.errors()]
        return error_response(422, "validation_error", "Request validation failed", details)

    @app.get("/", tags=["system"])
    def root(): return {"status": "running", "service": configured.app_name}
    @app.get("/health", tags=["system"])
    def health(): return {"status": "ok"}
    @app.get("/ready", tags=["system"])
    def ready():
        if not db.ready(): return error_response(503, "not_ready", "Database is unavailable")
        return {"status": "ready"}
    return app

app = create_app()

if __name__ == "__main__":
    runtime = get_settings()
    uvicorn.run("src.main:app", host=runtime.host, port=runtime.port, reload=runtime.debug)
