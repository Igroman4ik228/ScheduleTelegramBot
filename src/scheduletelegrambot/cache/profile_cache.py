from __future__ import annotations

from scheduletelegrambot.cache.cashews import CACHE_KEY_PREFIX, cache


class ProfileCache:
    async def create(self, user_id: int, bot_message_id: int, user_message_id: int) -> None:
        await cache.set(
            self._key(user_id),
            (bot_message_id, user_message_id),
            expire="1d",
        )

    async def pop(self, user_id: int) -> tuple[int, int] | None:
        key = self._key(user_id)
        value = await cache.get(key)
        await cache.delete(key)
        return value

    @staticmethod
    def _key(user_id: int) -> str:
        return f"{CACHE_KEY_PREFIX}:profile:{user_id}"
