from datetime import datetime, timedelta


def calc_subscribe_end_time(duration_days: int) -> datetime:
    return datetime.now() + timedelta(days=duration_days)
