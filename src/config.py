"""Application configuration with an isolated environment namespace."""
from functools import lru_cache
from pathlib import Path
from pydantic import Field, SecretStr
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
    # PlayFab is an optional integration for a title owned by this server's
    # operator. The secret is loaded from DPS_PLAYFAB_SECRET_KEY and is never
    # serialized as plain text by Pydantic.
    playfab_title_id: str | None = Field(default=None, pattern=r"^[A-Za-z0-9]+$")
    playfab_secret_key: SecretStr | None = None
    playfab_timeout_seconds: float = Field(default=5.0, ge=0.5, le=30.0)

    @property
    def playfab_enabled(self) -> bool:
        return bool(self.playfab_title_id and self.playfab_secret_key)

    @model_validator(mode="after")
    def keep_debug_local(self):
        if self.debug and self.host.casefold() not in {"127.0.0.1", "::1", "localhost"}:
            raise ValueError("debug mode may only bind to a loopback host")
        if bool(self.playfab_title_id) != bool(self.playfab_secret_key):
            raise ValueError("PlayFab title ID and secret key must be configured together")
        return self

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
