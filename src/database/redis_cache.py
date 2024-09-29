import redis


def create_redis():
    # default localhost connection
    return redis.Redis(host='localhost', port=6379, db=0)


class ScheduleCache:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def create_schedule(self, weekday: int, group_name: str, schedule_data: str):
        key = f"schedule_{weekday}_{group_name}"

        # ex=86400 - set TTL(seconds) = 24 hours
        self.redis.set(key, schedule_data, ex=86400)

    def get_schedule(self, weekday: int, group_name: str):
        key = f"schedule_{weekday}_{group_name}"

        schedule_data = self.redis.get(key)

        if schedule_data is None:
            return None

        schedule_data = schedule_data.decode('utf-8')
        return schedule_data
