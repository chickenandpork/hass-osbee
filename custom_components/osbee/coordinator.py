"""The OSBee Hub correlates to a single UpdateCoordinator each."""

from datetime import timedelta
import logging

from async_timeout import timeout

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class OSBeeHubCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass, my_api):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="OSBee Hub",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=3),
        )
        self.my_api = my_api
        _LOGGER.debug("In coordinator.py::OSBeeHubCoordinator::__init__")

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with timeout(10):
                # Grab active context variables to limit data required to be fetched from API
                # Note: using context is not required if there is no need or ability to limit
                # data retrieved from API.
                _LOGGER.debug(
                    "In coordinator.py::OSBeeHubCoordinator::_async_update_data"
                )
                listening_idx = set(self.async_contexts())
                return await self.my_api.fetch_data(listening_idx)
        except Exception as e:  # pylint: disable=broad-exception-caught
            _LOGGER.exception(
                "In coordinator.py::OSBeeHubCoordinator::Exception on api::fetch_data %s",
                e,
            )
