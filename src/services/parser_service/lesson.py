from dataclasses import dataclass
from datetime import time as dt_time

from utils import constants


@dataclass
class Lesson:
    number: int
    time: dt_time | None
    subject: str
    classroom: str
    is_replacement: bool = False

    def to_dict(self):
        return {
            'numbers': self.number,
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
            number=data['number'],
            time=time_value,
            subject=data['subject'],
            classroom=data['classroom'],
            is_replacement=data.get('is_replacement', False)
        )

    @staticmethod
    def get_lesson_number_by_time(time: dt_time) -> int:
        lesson_times: list[dt_time] = []
        for lesson_time in constants.START_LESSONS_TIME:
            lesson_times.append(lesson_time)

        for i, lesson_time in enumerate(lesson_times):
            if time <= lesson_time:
                return i

        return len(constants.START_LESSONS_TIME)

    def __str__(self) -> str:
        return f"{self.number} {self.time} {self.subject} {self.classroom} {self.is_replacement}"
