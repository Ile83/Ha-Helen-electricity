import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN  # Assuming you've defined the domain in a `const.py` file

class MyElectricityConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        
        if user_input is not None:
            # Here you could validate the input, such as verifying the API keys are correct
            return self.async_create_entry(title="My Electricity", data=user_input)

        data_schema = vol.Schema({
            vol.Required("client_id"): str,
            vol.Required("client_secret"): str,
            vol.Required("subscription_key"): str,
            vol.Required("meter_point_id"): str,
        })

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

