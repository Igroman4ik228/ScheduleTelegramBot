
from datetime import time as dt_time

import constants


class Lesson():

    def __init__(self,
                 group: str,
                 numbers: list[int],
                 time: tuple[int, int],
                 subject: str,
                 classroom: str,
                 is_replacement=False):
        self.group = group
        self.numbers = numbers
        self.time = time
        self.subject = subject
        self.classroom = classroom
        self.is_replacement = is_replacement

    def __str__(self) -> str:
        return f"{self.group} {self.numbers} {self.time} {self.subject} {self.classroom} {self.is_replacement}"

    @staticmethod
    def get_lesson_number_by_time(time: tuple[int, int]) -> int:
        input_time = dt_time(time[0], time[1])

        lesson_times = [time(hour, minute)
                        for hour, minute in constants.START_LESSONS_TIME]

        for i, lesson_time in enumerate(lesson_times):
            if input_time <= lesson_time:
                return i

        return len(constants.START_LESSONS_TIME)
