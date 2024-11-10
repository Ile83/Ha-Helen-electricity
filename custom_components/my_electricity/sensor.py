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
        self._state = None
        self.meter_point_id = meter_point_id

    @property
    def state(self):
        return self.coordinator.data.get(self.meter_point_id)

    async def async_update(self):
        await self.coordinator.async_request_refresh()

async def async_setup_entry(hass, config_entry, async_add_entities):
    meter_point_id = config_entry.data.get("meter_point_id")
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="electricity usage",
        update_method=lambda: fetch_data(meter_point_id),
        update_interval=timedelta(minutes=30),
    )

    await coordinator.async_refresh()
    async_add_entities([ElectricitySensor(coordinator, meter_point_id)])

def rate_limit():
    current_time = time.time()
    # Remove timestamps older than 60 seconds
    global last_called_times
    last_called_times = [t for t in last_called_times if current_time - t < 60]
    if len(last_called_times) >= RATE_LIMIT:
        raise UpdateFailed("Rate limit exceeded. Please try again later.")
    last_called_times.append(current_time)

async def fetch_data(meter_point_id):
    try:
        rate_limit()  # Apply rate limiting before making the request
        headers = {
            "Authorization": "Bearer YOUR_TOKEN",
            "Ocp-Apim-Subscription-Key": "YOUR_SUBSCRIPTION_KEY"
        }
        params = {
            "meteringPointId": meter_point_id,
            "startTime": "2023-01-01T00:00:00Z",
            "endTime": "2023-12-31T23:59:59Z",
            "resultStep": "DAY"
        }
        response = requests.get(API_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        # Extract the kWh usage for the specific meter point
        time_series = data.get("timeSeriesResult", {}).get("timeSeries", {})
        if time_series:
            return {meter_point_id: time_series.get("sum")}
        raise UpdateFailed(f"Meter point ID {meter_point_id} not found in response.")
    except requests.exceptions.HTTPError as http_err:
        _LOGGER.error(f"HTTP error occurred: {http_err}")
        raise UpdateFailed(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        _LOGGER.error(f"Connection error occurred: {conn_err}")
        raise UpdateFailed(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        _LOGGER.error(f"Timeout error occurred: {timeout_err}")
        raise UpdateFailed(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        _LOGGER.error(f"Request error occurred: {req_err}")
        raise UpdateFailed(f"Request error occurred: {req_err}")