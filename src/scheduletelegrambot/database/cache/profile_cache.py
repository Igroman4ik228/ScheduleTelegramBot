from __future__ import annotations

from typing import TYPE_CHECKING

from scheduletelegrambot.database.cache.cashews import CACHE_KEY_PREFIX

if TYPE_CHECKING:
    from cashews import Cache


class ProfileCache:
    def __init__(self, cache: Cache) -> None:
        self.cache = cache

    async def create(self, user_id: int, bot_message_id: int, user_message_id: int) -> None:
        await self.cache.set(
            self._key(user_id),
            (bot_message_id, user_message_id),
            expire="1d",
        )

    async def pop(self, user_id: int) -> tuple[int, int] | None:
        key = self._key(user_id)
        value = await self.cache.get(key)
        await self.cache.delete(key)
        return value

    @staticmethod
    def _key(user_id: int) -> str:
        return f"{CACHE_KEY_PREFIX}:profile:{user_id}"
