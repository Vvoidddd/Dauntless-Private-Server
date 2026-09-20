"""Application configuration with an isolated environment namespace."""
from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DPS_", env_file=".env", env_file_encoding="utf-8", extra="ignore")
    app_name: str = "Dauntless Private Server"
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1, le=65535)
    database_path: Path = Path("data/server.db")
    session_ttl_seconds: int = Field(default=86_400, ge=300, le=2_592_000)

    @model_validator(mode="after")
    def keep_debug_local(self):
        if self.debug and self.host.casefold() not in {"127.0.0.1", "::1", "localhost"}:
            raise ValueError("debug mode may only bind to a loopback host")
        return self

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
