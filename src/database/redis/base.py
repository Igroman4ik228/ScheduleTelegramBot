from logging import getLogger

from redis.asyncio import Redis

from utils.config import settings

redis_client = Redis.from_url(settings.redis_url)


class BaseCache:
    def __init__(self):
        self.redis = redis_client
        self.logger = getLogger(__class__.__name__)

    # ex=86400 - set TTL(seconds) = 24 hours
    async def create(self, key, value, ex=86400):
        await self.redis.set(key, value, ex=ex)

    async def hcreate(self, name: str, key, value):
        await self.redis.hset(name, key, value)

    async def get(self, key):
        return await self.redis.get(key)

    async def hget(self, name: str, key: str):
        return await self.redis.hget(name, key)

    async def delete(self, key):
        await self.redis.delete(key)
