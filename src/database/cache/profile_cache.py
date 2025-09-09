from redis.asyncio import Redis

from database.cache.base import BaseRedis


class ProfileCache(BaseRedis):
    def __init__(self, redis: Redis):
        super().__init__(redis)

    async def create(
        self, user_id: int, bot_message_id: int, user_message_id: int
    ):
        """
        Create a profile for a given user id with bot message id and user message id
        in redis cache under the key "user:profile".
        """
        profile_string = f"{bot_message_id}|{user_message_id}"
        await super().hcreate("user:profile", user_id, profile_string)

    async def get(self, user_id: int):
        """
        Returns:
            (bot message id, user message id) or None if user id is not found
        """
        profile_string = await super().hget("user:profile", user_id)
        if profile_string is None:
            return None

        # convert to number
        try:
            profile_string = profile_string.decode("utf-8")
            bot_mes_id, user_mes_id = profile_string.split("|", 1)

            bot_mes_id = int(bot_mes_id)
            user_mes_id = int(user_mes_id)
        except (ValueError, IndexError):
            return None

        return (bot_mes_id, user_mes_id)
