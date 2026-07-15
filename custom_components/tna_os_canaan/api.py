from __future__ import annotations

import asyncio
from typing import Any

from aiohttp import ClientSession, ClientTimeout

from .const import API_TIMEOUT


class TnaOsApiError(Exception):
    """Raised when the TNA-OS API returns an error or cannot be reached."""


class TnaOsClient:
    """Small async client for the unauthenticated TNA-OS-CANAAN HTTP API."""

    def __init__(self, session: ClientSession, host: str) -> None:
        self._session = session
        self.host = host.strip().removeprefix("http://").removeprefix("https://").rstrip("/")
        self.base_url = f"http://{self.host}"

    async def _request(self, method: str, path: str, json: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}{path}"
        try:
            async with self._session.request(
                method,
                url,
                json=json,
                timeout=ClientTimeout(total=API_TIMEOUT),
            ) as resp:
                data = await resp.json(content_type=None)
        except (asyncio.TimeoutError, OSError, Exception) as err:
            raise TnaOsApiError(f"TNA-OS API request failed: {err}") from err

        if isinstance(data, dict) and data.get("ok") is False:
            raise TnaOsApiError(str(data.get("err", "unknown API error")))
        return data

    async def info(self) -> dict[str, Any]:
        data = await self._request("GET", "/api/system/info")
        if not isinstance(data, dict):
            raise TnaOsApiError("Invalid /api/system/info response")
        return data

    async def asic(self) -> dict[str, Any]:
        data = await self._request("GET", "/api/system/asic")
        if not isinstance(data, dict):
            raise TnaOsApiError("Invalid /api/system/asic response")
        return data

    async def patch_system(self, payload: dict[str, Any]) -> None:
        await self._request("PATCH", "/api/system", json=payload)

    async def set_power(self, on: bool) -> None:
        await self._request("POST", "/api/system/power", json={"on": on})

    async def reboot(self) -> None:
        await self._request("POST", "/api/system/reboot")

    async def reset_board(self) -> None:
        await self._request("POST", "/api/board/0/reset")

    async def ping(self, target: str) -> dict[str, Any]:
        data = await self._request("POST", "/api/system/ping", json={"target": target})
        return data if isinstance(data, dict) else {"success": False, "rtt": 0}
