"""Vicktor Router conversation agent.

Routes every utterance deterministic-first:

    user text
       -> Home Assistant built-in agent  (commands + state questions; instant)
          |- understood?   -> return its answer (no LLM involved)
          |- no intent?    -> forward to the configured fallback LLM agent
                              (e.g. Vicktor = a local model + Muninn memory)

We override async_process directly (not _async_handle_message), which keeps the
router thin: each sub-agent manages its own chat session via async_converse, so
there is no ChatLog/session re-entrancy to juggle here.

"No match" is detected ONLY on an explicit NO_INTENT_MATCH error — so a state
question that the built-in agent *answered* (response_type QUERY_ANSWER) is
returned deterministically, and only genuine chat/recall/save falls through.
"""

from __future__ import annotations

import logging

from homeassistant.components import conversation
from homeassistant.components.conversation import (
    ConversationEntity,
    ConversationInput,
    ConversationResult,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.intent import IntentResponseErrorCode, IntentResponseType

from .const import CONF_FALLBACK_AGENT, CONF_PRIMARY_AGENT, DEFAULT_PRIMARY

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Register the router conversation entity for this config entry."""
    async_add_entities([VicktorRouterEntity(hass, entry)])


class VicktorRouterEntity(ConversationEntity):
    """Deterministic-first conversation router."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self._entry = entry
        self._attr_unique_id = entry.entry_id

    @property
    def name(self) -> str:
        return "Vicktor Router"

    @property
    def supported_languages(self) -> str:
        # "*" => support every language; appears for all assistants.
        return "*"

    def _cfg(self, key: str, default=None):
        return self._entry.options.get(key, self._entry.data.get(key, default))

    async def async_process(
        self, user_input: ConversationInput
    ) -> ConversationResult:
        primary = self._cfg(CONF_PRIMARY_AGENT, DEFAULT_PRIMARY)
        fallback = self._cfg(CONF_FALLBACK_AGENT)
        text = user_input.text

        result: ConversationResult | None = None

        # 1) Deterministic agent first: commands AND state questions.
        try:
            result = await conversation.async_converse(
                hass=self.hass,
                text=text,
                conversation_id=user_input.conversation_id,
                context=user_input.context,
                language=user_input.language,
                agent_id=primary,
            )
            resp = result.response
            no_match = (
                resp.response_type == IntentResponseType.ERROR
                and getattr(resp, "error_code", None)
                == IntentResponseErrorCode.NO_INTENT_MATCH
            )
            if not no_match:
                _LOGGER.debug(
                    "vicktor_router: handled locally (type=%s)", resp.response_type
                )
                return result
        except Exception as err:  # noqa: BLE001
            # A failure in the local agent must never block the LLM fallback.
            _LOGGER.warning(
                "vicktor_router: local agent error, falling back to LLM: %s", err
            )

        # 2) No local intent matched -> hand off to the LLM agent (chat + memory).
        if not fallback:
            _LOGGER.error("vicktor_router: no fallback agent configured")
            if result is not None:
                return result
            r = intent.IntentResponse(language=user_input.language)
            r.async_set_error(
                IntentResponseErrorCode.UNKNOWN,
                "Vicktor Router has no fallback agent configured.",
            )
            return ConversationResult(
                response=r, conversation_id=user_input.conversation_id
            )

        _LOGGER.debug("vicktor_router: no local match -> fallback %s", fallback)
        return await conversation.async_converse(
            hass=self.hass,
            text=text,
            conversation_id=user_input.conversation_id,
            context=user_input.context,
            language=user_input.language,
            agent_id=fallback,
        )
