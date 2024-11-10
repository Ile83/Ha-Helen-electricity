import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN

@config_entries.HANDLERS.register(DOMAIN)
class ElectricityConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        self.data = {}

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            self.data = user_input
            return self.async_create_entry(title="Helen Electricity", data=self.data)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("client_id"): str,
                    vol.Required("client_secret"): str,
                    vol.Required("meter_point_id"): str,
                    vol.Required("subscription_key"): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ElectricityOptionsFlowHandler(config_entry)

class ElectricityOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = {
            vol.Optional("update_interval", default=self.config_entry.options.get("update_interval", 30)): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=1440)
            ),
        }

        return self.async_show_form(step_id="init", data_schema=vol.Schema(options))
