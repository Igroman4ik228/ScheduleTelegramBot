from redis.asyncio import Redis


def create_redis(
    host: str = 'localhost',
    port: int = 6379,
    db: int = 0,
    password: str | None = None
) -> Redis:
    if password is not None:
        return Redis.from_url(f"redis://{host}:{password}{port}/{db}")
    return Redis.from_url(f"redis://{host}:{port}/{db}")


redis_client = create_redis()


class BaseCache:
    def __init__(self):
        self.redis = redis_client

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
