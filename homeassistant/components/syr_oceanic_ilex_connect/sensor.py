"""Sensor component for Syr Oceanic water filter system via Ilex Connect."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfPressure, UnitOfTime, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

if TYPE_CHECKING:
    from . import ILexConfigEntry
from .const import DOMAIN
from .coordinator import ILexDataUpdateCoordinator

SENSOR_MAP = [
    {"translation_key": "water_pressure", "key": "getPRS", "unit": UnitOfPressure.BAR},
    {"translation_key": "current_flow", "key": "getFLO", "unit": UnitOfVolume.LITERS},
    {
        "translation_key": "remaining_capacity",
        "key": "getRES",
        "unit": UnitOfVolume.LITERS,
    },
    {
        "translation_key": "water_used_today",
        "key": "getUWF",
        "unit": UnitOfVolume.CUBIC_METERS,
    },
    {"translation_key": "days_remaining", "key": "getRPD", "unit": UnitOfTime.DAYS},
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ILexConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Syr Oceanic sensors based on a config entry."""
    coordinator: ILexDataUpdateCoordinator = entry.runtime_data
    entities: list[ILexSensor] = []
    for serial in coordinator.data:
        entities.extend(
            ILexSensor(coordinator, serial, sensor_def) for sensor_def in SENSOR_MAP
        )
    async_add_entities(entities)


class ILexSensor(SensorEntity):
    """Representation of a Syr Oceanic sensor."""

    def __init__(
        self,
        coordinator: ILexDataUpdateCoordinator,
        serial: str,
        sensor_def: dict[str, str],
    ) -> None:
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.serial = serial
        self.sensor_def = sensor_def
        self._attr_has_entity_name = True
        self._attr_translation_key = sensor_def["translation_key"]
        self._attr_unique_id = f"{serial}_{sensor_def['key']}"
        self._attr_native_unit_of_measurement = sensor_def.get("unit")

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        value = self.coordinator.data[self.serial]["live"].get(self.sensor_def["key"])
        return float(value) if value not in (None, "") else None

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this sensor."""
        meta = self.coordinator.data[self.serial]["meta"]
        live = self.coordinator.data[self.serial]["live"]
        return DeviceInfo(
            identifiers={(DOMAIN, meta["serial"])},
            name=f"Syr Oceanic {meta['dtype']}",
            manufacturer="Syr / Oceanic",
            model=meta["dtype"],
            sw_version=live.get("firmware_version"),
        )
