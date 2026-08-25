from datetime import UTC, datetime, timedelta


def calc_subscribe_end_time(duration_days: int) -> datetime:
    return datetime.now(UTC) + timedelta(days=duration_days)
