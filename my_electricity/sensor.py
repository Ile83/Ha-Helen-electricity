import requests
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
import logging
import time

_LOGGER = logging.getLogger(__name__)
API_URL = "https://api.open.helen.fi/electricity-retail/v2/time-series"

# Rate limiting variables
RATE_LIMIT = 20  # Maximum calls per minute
last_called_times = []

class ElectricitySensor(SensorEntity):
    def __init__(self, coordinator, meter_point_id):
        self.coordinator = coordinator
        self._attr_name = f"Electricity Usage ({meter_point_id})"
        self._attr_unique_id = f"electricity_usage_{meter_point_id}"
        self.meter_point_id = meter_point_id

        _LOGGER.info(f"Initialized ElectricitySensor for meter_point_id: {meter_point_id}")

    @property
    def state(self):
        return self.coordinator.data.get(self.meter_point_id)

    async def async_update(self):
        _LOGGER.debug(f"Updating state for meter_point_id: {self.meter_point_id}")
        await self.coordinator.async_request_refresh()

async def async_setup_entry(hass, config_entry, async_add_entities):
    # Retrieve configuration details from config_entry
    meter_point_id = config_entry.data.get("meter_point_id")
    subscription_key = config_entry.data.get("subscription_key")
    api_key = config_entry.data.get("api_key")
    client_secret = config_entry.data.get("client_secret")

    # Logging for troubleshooting
    _LOGGER.info(f"Setting up entity for meter_point_id: {meter_point_id}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="electricity usage",
        update_method=lambda: fetch_data(meter_point_id, subscription_key, api_key, client_secret),
        update_interval=timedelta(minutes=1),
    )

    await coordinator.async_refresh()
    async_add_entities([ElectricitySensor(coordinator, meter_point_id)])

def rate_limit():
    current_time = time.time()
    # Remove timestamps older than 60 seconds
    global last_called_times
    last_called_times = [t for t in last_called_times if current_time - t < 60]
    if len(last_called_times) >= RATE_LIMIT:
        _LOGGER.warning("Rate limit exceeded. Please try again later.")
        raise UpdateFailed("Rate limit exceeded. Please try again later.")
    last_called_times.append(current_time)
    _LOGGER.debug(f"Rate limit check passed. Current API call count: {len(last_called_times)}")

async def fetch_data(meter_point_id, subscription_key, api_key, client_secret):
    try:
        rate_limit()  # Apply rate limiting before making the request
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Ocp-Apim-Subscription-Key": subscription_key
        }
        params = {
            "meteringPointId": meter_point_id,
            "startTime": "2023-01-01T00:00:00Z",
            "endTime": "2023-12-31T23:59:59Z",
            "resultStep": "DAY"
        }
        _LOGGER.info(f"Fetching data for meter_point_id: {meter_point_id}")
        response = requests.get(API_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        # Log the response for debugging purposes
        _LOGGER.debug(f"API response: {data}")

        # Extract the kWh usage for the specific meter point
        time_series = data.get("timeSeriesResult", {}).get("timeSeries", {})
        if time_series:
            usage_sum = time_series.get("sum")
            _LOGGER.info(f"Fetched electricity usage sum for meter_point_id: {meter_point_id}: {usage_sum}")
            return {meter_point_id: usage_sum}
        _LOGGER.error(f"Meter point ID {meter_point_id} not found in response.")
        raise UpdateFailed(f"Meter point ID {meter_point_id} not found in response.")
    except requests.exceptions.RequestException as req_err:
        _LOGGER.error(f"Request error occurred: {req_err}")
        raise UpdateFailed(f"Request error occurred: {req_err}")
