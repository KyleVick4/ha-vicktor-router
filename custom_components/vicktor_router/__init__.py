"""Vicktor Router — deterministic-first conversation router for Home Assistant.

Each utterance is tried against Home Assistant's built-in agent first (commands
and state questions resolve instantly and deterministically). Anything the
built-in agent doesn't understand falls through to a configured LLM agent
(e.g. Vicktor = a local Ollama model + Muninn memory) for chat and recall/save.

The real work lives in conversation.py; this module just wires the config
entry to the conversation platform.
"""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["conversation"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Vicktor Router from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry and remove the router agent."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the integration when the user saves new options."""
    await hass.config_entries.async_reload(entry.entry_id)
