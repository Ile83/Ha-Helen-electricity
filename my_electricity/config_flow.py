from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN  # Assuming you have a const.py file for constants
from homeassistant.helpers import config_validation as cv
from homeassistant.const import CONF_API_KEY
token = hass.data.get("secrets", {}).get("token")
subscription_key = hass.data.get("secrets", {}).get("subscription_key")
client_secret = hass.data.get("secrets", {}).get("client_secret")


@config_entries.HANDLERS.register(DOMAIN)
class ElectricityConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Validation logic can go here if necessary
            return self.async_create_entry(title="Electricity Usage", data=user_input)

        # Define the schema for user input in the config flow UI
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("subscription_key"): str,
                vol.Required("api_key"): str,
                vol.Required("client_secret"): str,
            }),
            errors=errors
        )

