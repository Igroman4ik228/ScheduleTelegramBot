from database.redis.base import BaseCache


class ScheduleCache(BaseCache):
    def create(self, weekday: int, group_name: str, schedule: str):
        """
        Creates a schedule in redis cache
        """
        key = f"schedule_{weekday}_{group_name}"
        super().create(key, schedule)

    def get(self, weekday: int, group_name: str) -> str | None:
        """
        Gets a schedule from redis cache by weekday and group name
        """
        key = f"schedule_{weekday}_{group_name}"

        schedule_data = super().get(key)
        if schedule_data is None:
            return None

        schedule_data = schedule_data.decode('utf-8')
        return schedule_data
