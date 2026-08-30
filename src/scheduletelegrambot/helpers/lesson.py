from dataclasses import dataclass, field
from datetime import time as dt_time

from scheduletelegrambot.helpers.week import Week
from scheduletelegrambot.utils.constants import END_LESSONS_TIME, START_LESSONS_TIME


@dataclass(frozen=True)
class TeachingAssignment:
    teacher: str
    classrooms: tuple[str, ...]


@dataclass
class Lesson:
    number: int
    time: dt_time | None
    subject: str
    teaching_assignments: list[TeachingAssignment] = field(default_factory=list)
    is_replacement: bool = False

    @staticmethod
    def get_lesson_number(time: dt_time) -> int:
        for number, lesson_time in enumerate(START_LESSONS_TIME):
            if time <= lesson_time:
                return number
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
