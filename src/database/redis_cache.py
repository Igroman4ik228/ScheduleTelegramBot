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


class ProfileCache:
    def __init__(self, redis_client):
        self.redis = redis_client

    def create_profile(self, user_id, bot_mes_id, user_mes_id):
        profile_string = f"{bot_mes_id}|{user_mes_id}"
        self.redis.hset("user:profile", user_id, profile_string)

    def get_profile(self, user_id):
        """
        Out:
        (bot_mes_id, user_mes_id)
        """
        profile_string = self.redis.hget(f"user:profile", user_id)

        if profile_string is None:
            return None

        # convert to number
        try:
            profile_string = profile_string.decode('utf-8')
            bot_mes_id, user_mes_id = profile_string.split('|', 1)

            bot_mes_id = int(bot_mes_id)
            user_mes_id = int(user_mes_id)
        except (ValueError, IndexError):
            return None

        return (bot_mes_id, user_mes_id)
