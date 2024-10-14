from redis import Redis


def create_redis():
    # default localhost connection
    return Redis(host='localhost', port=6379, db=0)


class BaseCache:
    def __init__(self, redis: Redis):
        self.redis = redis

    # ex=86400 - set TTL(seconds) = 24 hours
    def create(self, key, value, ex=86400):
        self.redis.set(key, value, ex=ex)

    def hcreate(self, name: str, key, value):
        self.redis.hset(name, key, value)

    def get(self, key):
        return self.redis.get(key)

    def hget(self, name: str, key: str):
        return self.redis.hget(name, key)

    def delete(self, key):
        self.redis.delete(key)
