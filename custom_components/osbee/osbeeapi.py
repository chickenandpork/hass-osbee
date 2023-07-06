"""Wrapper class for OSBee's API.

OSBee API is a bit unusual; OSBeeAPI class wraps the OSBee API to collect and simplify the
protocol's oddities.  For more info, see:

https://github.com/OpenSprinkler/OSBeeWiFi-Firmware/blob/master/docs/firmware1.0.0/OSBeeAPI1.0.0.pdf
"""

import aiohttp
import logging
from threading import Lock

_LOGGER = logging.getLogger(__name__)


class OSBeeAPI:
    """aiohttp facade for API requests to OSB Hub device."""

    def __init__(self, host, session: aiohttp.ClientSession) -> None:
        """Create an OSBeeAPI by offering a host, and an async session to get there."""
        self._host = host
        self._jc_cache = None
        self._session = session
        self.lock = Lock()

    async def fetch_data(self, index):
        """Get raw device state from the OSBee Hub via API.  No authentication yet considered."""
        _LOGGER.warning("Fetch_data from %s with index %s", self._host, index)
        async with self._session.get(f"http://{self._host}/jc") as jc_request:
            if jc_request.status == 401:
                raise AuthenticationError("Unable to authenticate with the OSBee API")

            if jc_request.status == 500:
                raise ServiceUnavailableError("The service is currently unavailable")

            if jc_request.status == 429:
                raise TooManyRequestsError(
                    "Too many requests have been made to the API"
                )

            if jc_request.status != 200:
                raise Exception(  # pylint: disable=broad-exception-raised
                    "Error connecting to OSBee Hub"
                )

            jc_body = await jc_request.json(content_type="text/html")
            if len(jc_body) == 0:
                raise Exception(  # pylint: disable=broad-exception-raised
                    "The server returned a zero-length body, not a valid response"
                )

            self._jc_cache = jc_body
            return jc_body  # the resulting structure has no conventional "data" element, just raw JSON

    async def async_turn_off(self, zone_id):
        """Async entry point to deactivate the valve/relay for the zone."""

        if not self._jc_cache:
            # too soon: status not yet pulled somehow
            pass
        else:
            # use jc_cache[zbits] to avoid WET variables
            with self.lock:
                current = self._jc_cache["zbits"]
                _LOGGER.warning("In turn_off: current state is %s", current)
                mask = 1 << zone_id
                self._jc_cache["zbits"] = current & ~mask
            _LOGGER.warning("In turn_off: new state is %s", self._jc_cache["zbits"])

        return await self.async_apply_state()

    async def async_turn_on(self, zone_id):
        """Async entry point to activate the valve/relay for the zone."""

        if not self._jc_cache:
            # too soon: status not yet pulled somehow
            pass
        else:
            # use jc_cache[zbits] to avoid WET variables
            with self.lock:
                current = self._jc_cache["zbits"]
                _LOGGER.warning("In turn_on: current state is %s", current)
                mask = 1 << zone_id
                self._jc_cache["zbits"] = current | mask
            _LOGGER.warning("In turn_on: new state is %s", self._jc_cache["zbits"])

        return await self.async_apply_state()

    async def async_apply_state(self):
        """Async entry point to set active zones."""

        # firmware-1.0.0, part 11: Run Program (rp): http://devip/rp?dkey=xxx&pid=x&...
        # ...
        # When pid=77 (ASCII value of 'M'), this command starts a manual program.  You will need to supply two additional parameters:
        #  - zbits=x: zone enable bits (e.g. zbits=4 means zone 3 will turn on)
        #  - dur=x: duration (in seconds)
        #  - Example: pid=77&zbits=3&dur=300 turns on zones 1 and 2 manually for 5 minutes

        if self._jc_cache["zbits"] == 0:  # on zbits==0, we need to actually reset
            url = f"http://{self._host}/cc?dkey=opendoor&reset=1"
        else:
            new_bitz = self._jc_cache["zbits"]  # avoid triple-quoting
            url = f"http://{self._host}/rp?dkey=opendoor&pid=77&zbits={new_bitz}&dur={30*60}"

        async with self._session.get(url) as rp_request:
            if rp_request.status == 401:
                raise AuthenticationError(
                    "Unable to authenticate with the OSBee API"
                )

            if rp_request.status == 500:
                raise ServiceUnavailableError(
                    "The service is currently unavailable"
                )

            if rp_request.status == 429:
                raise TooManyRequestsError(
                    "Too many requests have been made to the API"
                )

            if rp_request.status != 200:
                raise Exception(  # pylint: disable=broad-exception-raised
                    "Error connecting to OSBee Hub"
                )

        _LOGGER.debug("In turn_off: finished")
        return await self.fetch_data(0)


class AuthenticationError(Exception):
    """Wrapper to allow try/except blocks to catch errors due to authentication that we don't have (HTTP code 401)."""


class ServiceUnavailableError(Exception):
    """Wrapper to allow try/except blocks to catch errors due to offline API (HTTP code 500)."""


class TooManyRequestsError(Exception):
    """Wrapper to allow try/except blocks to catch errors due to overloading an API (HTTP code 429)."""
