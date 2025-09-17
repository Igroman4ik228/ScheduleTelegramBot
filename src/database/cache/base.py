from abc import ABC, abstractmethod
from typing import Any

from redis.asyncio import Redis
from redis.typing import EncodableT, ExpiryT, KeyT, PatternT

from utils.constants import CacheTTL
from utils.logger import LoggerMixin


class ICache(ABC):
    @abstractmethod
    async def create(self, key, value, ex=CacheTTL.DEFAULT.value): ...

    @abstractmethod
    async def get(self, key): ...

    @abstractmethod
    async def delete(self, key): ...

    @abstractmethod
    async def close(self): ...

    @abstractmethod
    async def delete_by_pattern(self, pattern): ...


class BaseRedis(ICache, LoggerMixin):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def create(
        self, key: KeyT, value: EncodableT, ex: ExpiryT = CacheTTL.DEFAULT.value
    ):
        return await self.redis.set(key, value, ex=ex)

    async def hcreate(self, name: str, key, value) -> int:
        return await self.redis.hset(name, key, value)

    async def get(self, key: KeyT) -> Any:
        return await self.redis.get(key)

    async def hget(self, name: str, key: str) -> str | None:
        return await self.redis.hget(name, key)

    async def delete(self, key: KeyT) -> Any:
        return await self.redis.delete(key)

    async def delete_by_pattern(self, pattern: PatternT) -> Any | None:
        keys = self.redis.keys(pattern)
        if not keys:
            self.logger.warning(f"Delete key not found for pattern: {pattern}")
            return
        return await self.redis.delete(keys)

    async def close(self):
        return await self.redis.aclose()
