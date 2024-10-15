from dataclasses import dataclass

from redis import Redis

from database.redis.profile_cache import ProfileCache
from database.redis.schedule_cache import ScheduleCache


@dataclass
class Cache:
    redis: Redis = None

    @property
    def schedule(self) -> ScheduleCache:
        return ScheduleCache(self.redis)

    @property
    def profile(self) -> ProfileCache:
        return ProfileCache(self.redis)
