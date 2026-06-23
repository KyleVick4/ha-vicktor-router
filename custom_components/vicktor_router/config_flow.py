"""Config + options flow for Vicktor Router.

A single setting: which conversation agent to fall back to when Home
Assistant's built-in agent doesn't understand the utterance.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import CONF_FALLBACK_AGENT, DOMAIN


def _schema(defaults: dict) -> vol.Schema:
    """Form schema: pick the fallback conversation agent."""
    return vol.Schema(
        {
            vol.Required(
                CONF_FALLBACK_AGENT,
                default=defaults.get(CONF_FALLBACK_AGENT),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="conversation")
            ),
        }
    )


class VicktorRouterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Initial setup flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(title="Vicktor Router", data=user_input)

        return self.async_show_form(step_id="user", data_schema=_schema({}))

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return VicktorRouterOptionsFlow(config_entry)


class VicktorRouterOptionsFlow(config_entries.OptionsFlow):
    """Edit the fallback agent after setup."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = {**self._config_entry.data, **self._config_entry.options}
        return self.async_show_form(step_id="init", data_schema=_schema(current))
