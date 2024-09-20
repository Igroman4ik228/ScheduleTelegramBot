import json

from database.repositories.default_schedule import DefaultScheduleRepository
from database.repositories.result_schedule import ResultScheduleRepository
from ParserService.lesson import Lesson


class Builder():

    def __init__(self, replacement_lessons: list[Lesson], weekday: int, shift: int, ):
        self.replacement_lessons = replacement_lessons
        self.default_lessons = [
            Lesson(group='ИС1-31', numbers=[3], time=None,
                   subject='Математика', classroom='Аудитория 1'),
            Lesson(group='СД2-22', numbers=[2, 3, 4, 5], time=None,
                   subject='Физика', classroom='Аудитория 2'),
            Lesson(group='ДИ1-31', numbers=[1, 3, 5], time=None,
                   subject='Химия', classroom='Аудитория 3'),
            Lesson(group='СА1-1', numbers=[2], time=None,
                   subject='Биология', classroom='Аудитория 4'),
        ]
        self.weekday = weekday
        self.shift = shift
        self.default_schedule_rep = DefaultScheduleRepository()
        self.result_schedule_rep = ResultScheduleRepository()

    def _get_default_schedule(self) -> list[Lesson]:
        default_schedule_data = self.default_schedule_rep.get(self.shift,
                                                              self.weekday)
        if default_schedule_data is None:
            return []

        return [Lesson.from_dict(lesson) for lesson in json.loads(default_schedule_data)]

    def format_schedule(self, result_schedule: list[Lesson]) -> str:
        return json.dumps([lesson.to_dict() for lesson in result_schedule])

    def save_schedule_to_db(self, result_schedule: str):
        for lesson in result_schedule:
            self.result_schedule_rep.create(self.weekday, lesson, lesson.group)
