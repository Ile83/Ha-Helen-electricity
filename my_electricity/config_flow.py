from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol

from .const import DOMAIN

class ElectricityUsageConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Electricity Usage integration."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate user input here if needed, then proceed
            return self.async_create_entry(title="Electricity Usage", data=user_input)

        # Define the schema of the configuration form
        data_schema = vol.Schema({
            vol.Required("client_id"): str,
            vol.Required("client_secret"): str,
            vol.Required("subscription_key"): str,
            vol.Optional("enable_pricing", default=False): bool,
            vol.Optional("rate_limit", default=20): int,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ElectricityUsageOptionsFlowHandler(config_entry)

class ElectricityUsageOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an options flow for Electricity Usage integration."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema({
            vol.Optional("enable_pricing", default=self.config_entry.options.get("enable_pricing", False)): bool,
            vol.Optional("rate_limit", default=self.config_entry.options.get("rate_limit", 20)): int,
        })

        return self.async_show_form(step_id="init", data_schema=options_schema)
