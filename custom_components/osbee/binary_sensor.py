"""OSBee Binary Sensor shows state of a valve/zone."""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.components.binary_sensor import (
    PLATFORM_SCHEMA,
    BinarySensorEntity,
)
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN
from .coordinator import OSBeeHubCoordinator
from .osbeeapi import OSBeeAPI

DEFAULT_NAME = "OSBee - Binary Sensor"

_LOGGER = logging.getLogger(__name__)


def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Your controller/hub specific code."""

    _LOGGER.debug("In binary_sensor.py::setup")

    return True


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        # vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

#
# The hass.data structure for this platform looks like (for example 192.168.1.77 is macaddr 1a:2b:3c:4d:5e:6f)
#
# hass.data[DOMAIN]: {
#     "192.168.1.77": {
#         "h": an OSBeeAPI ("192.168.1.77", <async_client session>)
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
    """Set up the OSBee platform for binary_sensor.

    The async_setup_platform in binary_sensor for osbee is is a complete copy of the same in
    sensor, which risks skew and incompatibility (WET not DRY) so will eventually need to be
    reconciled.
    """

    _LOGGER.debug("In binary_sensor.py::async_setup_platform: config is %s", config)
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {"coordinators": {}, "hubs": {}}
    if config[CONF_HOST] not in hass.data[DOMAIN]["hubs"]:
        h = OSBeeAPI(config[CONF_HOST], async_create_clientsession(hass))
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
        "In binary_sensor.py::async_setup_platform: post-async_config_entry_first_refresh: data is %s",
        coordinator.data,
    )

    if coordinator.data:
        async_add_entities(
            [
                OSBeeZoneSensor(coordinator, zone_id, zone_name)
                for zone_id, zone_name in enumerate(coordinator.data["zons"])
            ]
        )


class OSBeeZoneSensor(CoordinatorEntity, BinarySensorEntity):
    """A binary_sensor using CoordinatorEntity to do most of the work.

    This Sensor indicates whether the zone is currently turned on -- water-flowing -- or off.

    The CoordinatorEntity class provides:
      should_poll
      async_update
      async_added_to_hass
      available

    """

    def __init__(self, coordinator, zone_id, zone_name):
        """Pass coordinator to CoordinatorEntity."""
        _LOGGER.debug(
            "In __init__::OSBeeZoneSensor::__init__: zone_id = %s",
            zone_id,
        )
        super().__init__(coordinator)
        self._zone_id = zone_id
        self._zone_name = zone_name
        self._mac = coordinator.data["mac"]

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        mask = 1 << self._zone_id
        self._attr_is_on = (self.coordinator.data["zbits"] & mask) > 0
        _LOGGER.debug(
            "In __init__::OSBeeZoneSensor::_handle_coordinator_update, zone_id = %d, mask = %d, data[zbits] = %s, value=%s",
            self._zone_id,
            mask,
            self.coordinator.data["zbits"],
            self._attr_is_on,
        )
        super()._handle_coordinator_update()

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        _LOGGER.debug("In __init__::OSBeeZoneSensor::unique_id")
        return f"""{self._mac.replace(":", "")}_zone_{self._zone_id}"""
