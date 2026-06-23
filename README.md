# Vicktor Router — deterministic-first conversation agent for Home Assistant

A tiny conversation agent that **routes** each utterance instead of sending
everything to an LLM:

```
user text
   -> Home Assistant built-in agent   (commands + state questions: instant, deterministic)
      |- understood?  -> return its answer        ("turn off the light", "is the light on?", "what's the temp?")
      |- no intent?   -> forward to your LLM agent (chat, recall, remember, anything conversational)
```

## Why

Local LLMs are great at conversation and memory but unreliable at answering
"is the kitchen light on?" — Home Assistant hands them the *entire* home state
(`GetLiveContext`) and a small model can't pick out the one value. Home
Assistant's built-in agent answers those **instantly and correctly**; it just
isn't consulted for *questions* when an LLM is the conversation agent (only
commands take the local path). This router fixes that: the built-in agent gets
first crack at **everything**, and the LLM only handles what the built-in agent
genuinely doesn't understand.

Bonus: your house keeps working even if the LLM is slow or down — commands and
state questions never depend on it.

## Install (HACS)

1. HACS → ⋮ → **Custom repositories** → add `https://github.com/KyleVick4/ha-vicktor-router`, category **Integration**.
2. Install **Vicktor Router**, then **restart Home Assistant**.
3. **Settings → Devices & Services → Add Integration → Vicktor Router.**
4. Pick your **fallback conversation agent** — your LLM agent (e.g. the Ollama
   agent wired to your memory). Do **not** pick this router itself.
5. **Settings → Voice assistants →** edit your assistant → set the
   **Conversation agent** to **Vicktor Router**.

That's it. Commands and state questions now resolve deterministically; chat and
memory fall through to your LLM.

## Notes

- The primary agent is Home Assistant's built-in agent (`homeassistant`).
- "No match" is detected only on an explicit `NO_INTENT_MATCH`, so state-question
  answers (which come back as `QUERY_ANSWER`) are returned deterministically.
- Single instance; configurable later via the integration's **Configure** button.

MIT licensed. Built for the [Asgard](https://github.com/kylevick4/asgard) project.
