from abc import ABC, abstractmethod

from redis.asyncio import Redis
from redis.typing import EncodableT, ExpiryT, KeyT

from utils.constants import CacheTTL


class ICache(ABC):
    @abstractmethod
    async def create(self, key, value, ex=CacheTTL.DEFAULT.value): ...

    @abstractmethod
    async def get(self, key): ...

    @abstractmethod
    async def delete(self, key): ...

    @abstractmethod
    async def close(self): ...


class BaseRedis(ICache):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def create(
        self, key: KeyT, value: EncodableT, ex: ExpiryT = CacheTTL.DEFAULT.value
    ):
        return await self.redis.set(key, value, ex=ex)

    async def hcreate(self, name: str, key, value):
        return await self.redis.hset(name, key, value)

    async def get(self, key: KeyT):
        return await self.redis.get(key)

    async def hget(self, name: str, key: str):
        return await self.redis.hget(name, key)

    async def delete(self, key: KeyT):
        return await self.redis.delete(key)

    async def close(self):
        return await self.redis.aclose()
