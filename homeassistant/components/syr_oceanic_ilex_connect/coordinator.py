"""Data coordinator for Syr Oceanic i-Lex Connect."""

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ILexAuthError, ILexClient
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ILexDataUpdateCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Class to manage fetching Syr Oceanic data."""

    def __init__(
        self, hass: HomeAssistant, client: ILexClient, config_entry: ConfigEntry
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
            config_entry=config_entry,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Fetch data from API endpoint."""
        try:
            devices = await self.client.get_devices()
        except ILexAuthError as err:
            raise UpdateFailed(f"Authentication error: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        else:
            data = {}
            for device in devices["results"]:
                serial = device["serial"]
                live = await self.client.get_live_data(serial)
                data[serial] = {"meta": device, "live": live}
            return data
