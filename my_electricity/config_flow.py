from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN  # Assuming you have a const.py file for constants

class ElectricityConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # You can add validation here if needed
            return self.async_create_entry(title="Electricity Usage", data=user_input)

        # Define the schema for user input in the config flow UI
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("meter_point_id"): str,
                vol.Required("api_key"): str,
                vol.Required("access_token"): str,
            }),
            errors=errors
        )