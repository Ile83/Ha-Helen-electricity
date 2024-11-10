from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.service import async_register_admin_service

DOMAIN = "my_electricity"

async def async_setup(hass: HomeAssistant, config: ConfigType):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    # Register services defined in services.yaml
    async_register_admin_service(
        hass,
        DOMAIN,
        "update_usage",
        update_usage_service,
        schema=vol.Schema({"meter_point_id": str}),
    )
    async_register_admin_service(
        hass,
        DOMAIN,
        "reset_rate_limit",
        reset_rate_limit_service,
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    return True

async def update_usage_service(call):
    meter_point_id = call.data.get("meter_point_id")
    # Logic to manually update electricity usage for the specified meter_point_id
    # This would ideally invoke `fetch_data` and update the coordinator

async def reset_rate_limit_service(call):
    # Logic to reset the rate limit
    global last_called_times
    last_called_times.clear()