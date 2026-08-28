from __future__ import annotations

from cashews import Cache

CACHE_KEY_PREFIX = "schedule-bot:v1"

# A dedicated instance keeps this application's configuration isolated from
# Cashews' module-level default cache.
cache = Cache("schedule-telegram-bot")
