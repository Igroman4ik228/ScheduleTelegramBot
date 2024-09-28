
from dataclasses import dataclass
from datetime import time as dt_time

import constants


@dataclass
class Lesson:
    numbers: list[int]
    time: dt_time | None
    subject: str
    classroom: str
    is_replacement: bool = False

    def __str__(self) -> str:
        return f"{self.numbers} {self.time} {self.subject} {self.classroom} {self.is_replacement}"

    def to_dict(self):
        return {
            'numbers': self.numbers,
            'time': self.time.strftime("%H:%M") if self.time else None,
            'subject': self.subject,
            'classroom': self.classroom,
            'is_replacement': self.is_replacement
        }

    @staticmethod
    def from_dict(data: dict):
        time_value = dt_time.fromisoformat(
            data['time']
        ) if data['time'] else None

        return Lesson(
            numbers=data['numbers'],
            time=time_value,
            subject=data['subject'],
            classroom=data['classroom'],
            is_replacement=data.get('is_replacement', False)
        )

    @staticmethod
    def get_lesson_number_by_time(time: tuple[int, int]) -> int:
        input_time = dt_time(time[0], time[1])

        lesson_times = [dt_time(hour, minute)
                        for hour, minute in constants.START_LESSONS_TIME]

        for i, lesson_time in enumerate(lesson_times):
            if input_time <= lesson_time:
                return i

        return len(constants.START_LESSONS_TIME)


class Schedule:
    def __init__(self, group: str, lessons: list[Lesson] = []):
        self.group = group
        self.lessons = lessons
