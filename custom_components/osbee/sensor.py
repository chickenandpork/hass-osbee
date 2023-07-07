"""OSBee Sensor shows state of a hub."""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_TIMEOUT,
    SIGNAL_STRENGTH_DECIBELS,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import OSBeeHubCoordinator
from .osbeeapi import OSBeeAPI

DEFAULT_NAME = "OSBee - Sensor"

_LOGGER = logging.getLogger(__name__)


def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Your controller/hub specific code."""

    _LOGGER.debug("In sensor.py::setup")

    return True


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_TIMEOUT, default=1800): cv.positive_int,
        # vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

#
# The hass.data structure for this platform looks like (for example 192.168.1.77 is macaddr 1a:2b:3c:4d:5e:6f)
#
# hass.data[DOMAIN]: {
#     "192.168.1.77": {
#         "h": an OSBeeAPI ("192.168.1.77", 900, <async_client session>)
#         "c": an OSBeeHubCoordinator (hass, ^^ that OSBeeAPI)
#     }, ...
# }
#
# The UpdateCoordinator OSBeeHubCoordinator is defined at UpdateCoordinator, but in forma matches the `jc` from the OSBee:
# {
#     'fwv': 100,
#     'sot': 1,
#     'utct': 1687997732,
#     'pid': -1,
#     'tid': -1,
#     'np': 0,
#     'nt': 0,
#     'mnp': 6,
#     'prem': 0,
#     'trem': 0,
#     'zbits': 0,
#     'name': 'My OSBee WiFi',
#     'mac': 'C45BBE52F733',
#     'cid': 5437235,
#     'rssi': -71,
#     'zons': [
#         'Zone 1',
#         'Zone 2',
#         'Zone 3'
#     ]
# }


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the OSBee sensor platform."""

    _LOGGER.debug("In sensor.py::async_setup_platform: config is %s", config)
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {"coordinators": {}, "hubs": {}}
    if config[CONF_HOST] not in hass.data[DOMAIN]["hubs"]:
        h = OSBeeAPI(
            config[CONF_HOST],
            config[CONF_TIMEOUT] if CONF_TIMEOUT in config else 900,
            async_create_clientsession(hass),
        )
        c = OSBeeHubCoordinator(hass, h)

        hass.data[DOMAIN]["hubs"].update({config[CONF_HOST]: {"h": h, "c": c}})

    coordinator = hass.data[DOMAIN]["hubs"][config[CONF_HOST]]["c"]
    await coordinator.async_config_entry_first_refresh()

    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #

    # await coordinator.async_config_entry_first_refresh()

    _LOGGER.debug(
        "In sensor.py::async_setup_platform: post-async_config_entry_first_refresh: data is %s",
        coordinator.data,
    )

    if coordinator.data:
        for idx, ent in enumerate(coordinator.data):
            _LOGGER.debug(
                "In sensor.py::async_setup_platform: post-async_config_entry_first_refresh: idx %s, ent %s, val %s",
                idx,
                ent,
                coordinator.data[ent],
            )
        async_add_entities(
            OSBeeRSSISensor(coordinator, idx, ent)
            for idx, ent in enumerate(coordinator.data)
            if ent == "rssi"
        )


class OSBeeRSSISensor(CoordinatorEntity, SensorEntity):
    """A basic sensor using CoordinatorEntity to do most of the work.

    This RSSI Sensor is the simplest way to return data and show a "ping" -like behavior that the
    query to the OSBee device is functioning.

    The CoordinatorEntity class provides:
      should_poll
      async_update
      async_added_to_hass
      available

    """

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS

    def __init__(self, coordinator, idx, key):
        """Pass coordinator to CoordinatorEntity."""
        _LOGGER.debug(
            "In __init__::OSBeeRSSISensor::__init__: idx = %s, key = %s", idx, key
        )
        super().__init__(coordinator, context=idx)
        self.idx = idx
        self._key = key
        self._mac = coordinator.data["mac"]
        # self.name = "OSBee {} {}".format(self._mac,self._key)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug(
            "In __init__::OSBeeRSSISensor::_handle_coordinator_update, data = %s",
            self.coordinator.data,
        )
        self._attr_native_value = self.coordinator.data[self._key]
        super()._handle_coordinator_update()

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        _LOGGER.debug("In __init__::OSBeeRSSISensor::unique_id")
        return f"""{self._mac.replace(":", "")}_{self._key}"""
