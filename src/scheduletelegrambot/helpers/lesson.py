from dataclasses import dataclass
from datetime import time as dt_time
from typing import TYPE_CHECKING

from scheduletelegrambot.utils.constants import (
    END_LESSONS_TIME,
    START_LESSONS_TIME,
)

if TYPE_CHECKING:
    from scheduletelegrambot.helpers.week import Week


@dataclass
class Lesson:
    number: int
    time: dt_time | None
    subject: str
    classroom: str
    is_replacement: bool = False

    def to_dict(self):
        return {
            "numbers": self.number,
            "time": self.time.strftime("%H:%M") if self.time else None,
            "subject": self.subject,
            "classroom": self.classroom,
            "is_replacement": self.is_replacement,
        }

    @staticmethod
    def from_dict(data: dict):
        time_value = dt_time.fromisoformat(data["time"]) if data["time"] else None

        return Lesson(
            number=int(data["number"]),
            time=time_value,
            subject=data["subject"],
            classroom=data["classroom"],
            is_replacement=data.get("is_replacement", False),
        )

    @staticmethod
    def get_lesson_number(time: dt_time) -> int:
        lesson_times = list(START_LESSONS_TIME)

        for i, lesson_time in enumerate(lesson_times):
            if time <= lesson_time:
                return i

        return len(START_LESSONS_TIME)

    @staticmethod
    def get_start_time(lesson_number: int) -> dt_time:
        if lesson_number >= len(START_LESSONS_TIME):
            raise ValueError("Lesson number is out of range")
        return START_LESSONS_TIME[lesson_number]

    @staticmethod
    def get_end_time(lesson_number: int) -> dt_time:
        if lesson_number >= len(END_LESSONS_TIME):
            raise ValueError("Lesson number is out of range")
        return END_LESSONS_TIME[lesson_number]

    @staticmethod
    def get_full_time(lesson_number: int) -> str:
        start = Lesson.get_start_time(lesson_number).strftime("%H:%M")
        end = Lesson.get_end_time(lesson_number).strftime("%H:%M")
        return f"{start} - {end}"


@dataclass
class Schedule:
    week: Week
    group: str
    lessons: list[Lesson]
