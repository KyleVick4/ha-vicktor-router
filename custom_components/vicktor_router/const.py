"""Constants for the Vicktor Router integration."""

DOMAIN = "vicktor_router"

# Config keys
CONF_FALLBACK_AGENT = "fallback_agent"
CONF_PRIMARY_AGENT = "primary_agent"

# Home Assistant's built-in (deterministic) conversation agent — its entity id.
# NOTE: the legacy "homeassistant" agent id is rejected (400) on modern HA;
# the built-in agent must be addressed by its entity id.
DEFAULT_PRIMARY = "conversation.home_assistant"
