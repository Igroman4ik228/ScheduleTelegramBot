from datetime import timedelta
from logging import getLogger

from redis.asyncio import Redis

from utils.config import settings
from utils.constants import CacheTTL

redis_client = Redis.from_url(settings.redis_url())


class BaseCache:
    def __init__(self):
        self.logger = getLogger(self.__class__.__name__)
        self.redis = redis_client

    async def create(self, key, value, ex=CacheTTL.DEFAULT.value):
        await self.redis.set(key, value, ex=ex)

    async def hcreate(self, name: str, key, value):
        await self.redis.hset(name, key, value)

    async def get(self, key):
        return await self.redis.get(key)

    async def hget(self, name: str, key: str):
        return await self.redis.hget(name, key)

    async def delete(self, key):
        await self.redis.delete(key)
