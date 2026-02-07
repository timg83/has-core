"""API client for Syr Oceanic i-Lex Connect."""

from typing import Any

import aiohttp

from .const import BASE_URL, DEVICES_ENDPOINT, LOGIN_ENDPOINT


class ILexAuthError(Exception):
    """Exception for authentication errors."""


class ILexClient:
    """Client for interacting with the i-Lex Connect API."""

    def __init__(
        self, session: aiohttp.ClientSession, username: str, password: str
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._username = username
        self._password = password

    async def login(self) -> None:
        """Authenticate with the API."""
        async with self._session.post(
            f"{BASE_URL}{LOGIN_ENDPOINT}",
            json={"username": self._username, "password": self._password},
        ) as resp:
            if resp.status != 200:
                raise ILexAuthError("Login failed")
            data = await resp.json()
            if "redirect" not in data:
                raise ILexAuthError("Unexpected login response")

    async def get_devices(self) -> dict[str, Any]:
        """Get list of devices from the API."""
        async with self._session.get(
            f"{BASE_URL}{DEVICES_ENDPOINT}",
            params={"filterconnect": "online", "filterproducent": "oceanic"},
        ) as resp:
            if resp.status == 401:
                raise ILexAuthError("Session expired")
            return await resp.json()

    async def get_live_data(self, serial: str) -> dict[str, Any]:
        """Get live data for a specific device."""
        async with self._session.get(f"{BASE_URL}/api/devices/{serial}/live") as resp:
            if resp.status == 401:
                raise ILexAuthError("Session expired")
            return await resp.json()
