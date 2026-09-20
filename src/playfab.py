"""Small server-side client for an operator-owned PlayFab title.

This module intentionally implements no retail-client, Epic, EOS, or EAC
compatibility. The PlayFab developer key must remain on this backend.
"""
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.config import Settings


class PlayFabError(Exception):
    """A deliberately safe error suitable for conversion to an API response."""

    def __init__(self, code: str, message: str, status_code: int = 502):
        super().__init__(message)
        self.code, self.message, self.status_code = code, message, status_code


class PlayFabTransport(Protocol):
    async def post(self, url: str, headers: dict[str, str], payload: dict[str, Any], timeout: float) -> dict[str, Any]: ...


class UrlLibTransport:
    async def post(self, url: str, headers: dict[str, str], payload: dict[str, Any], timeout: float) -> dict[str, Any]:
        return await asyncio.to_thread(self._post, url, headers, payload, timeout)

    @staticmethod
    def _post(url: str, headers: dict[str, str], payload: dict[str, Any], timeout: float) -> dict[str, Any]:
        request = Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        try:
            with urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed HTTPS PlayFab host
                result = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            # Upstream bodies may contain sensitive or unstable details. Do not
            # pass them through to callers or logs.
            raise PlayFabError("playfab_rejected", "PlayFab rejected the request") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise PlayFabError("playfab_unavailable", "PlayFab is unavailable") from exc
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise PlayFabError("playfab_invalid_response", "PlayFab returned an invalid response") from exc
        if not isinstance(result, dict):
            raise PlayFabError("playfab_invalid_response", "PlayFab returned an invalid response")
        return result


@dataclass(frozen=True)
class PlayFabIdentity:
    playfab_id: str
    title_player_account_id: str | None


class PlayFabClient:
    def __init__(self, title_id: str | None, secret_key: str | None, timeout: float = 5.0, transport: PlayFabTransport | None = None):
        self.title_id = title_id.strip() if title_id else None
        self.__secret_key = secret_key
        self.timeout = timeout
        self.transport = transport or UrlLibTransport()

    @classmethod
    def from_settings(cls, settings: Settings) -> "PlayFabClient":
        secret = settings.playfab_secret_key.get_secret_value() if settings.playfab_secret_key else None
        return cls(settings.playfab_title_id, secret, settings.playfab_timeout_seconds)

    @property
    def enabled(self) -> bool:
        return bool(self.title_id and self.__secret_key)

    async def login_with_custom_id(self, custom_id: str) -> PlayFabIdentity:
        if not self.enabled:
            raise PlayFabError("playfab_disabled", "PlayFab integration is not configured", 503)
        url = f"https://{self.title_id}.playfabapi.com/Server/LoginWithCustomID"
        response = await self.transport.post(
            url,
            {"Content-Type": "application/json", "X-SecretKey": self.__secret_key or ""},
            {"CustomId": custom_id, "CreateAccount": True, "LoginTitlePlayerAccountEntity": True},
            self.timeout,
        )
        data = response.get("data")
        if not isinstance(data, dict) or not isinstance(data.get("PlayFabId"), str):
            raise PlayFabError("playfab_invalid_response", "PlayFab returned an invalid response")
        entity = data.get("EntityToken", {}).get("Entity", {}) if isinstance(data.get("EntityToken"), dict) else {}
        entity_id = entity.get("Id") if isinstance(entity, dict) and isinstance(entity.get("Id"), str) else None
        # SessionTicket and EntityToken are deliberately discarded. Linking an
        # identity does not require returning upstream credentials to a client.
        return PlayFabIdentity(playfab_id=data["PlayFabId"], title_player_account_id=entity_id)
