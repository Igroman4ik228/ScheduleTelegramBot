from database.repositories.default_schedule import DefaultScheduleRepository
from ParserService.lesson import Lesson


class builder():

    def __init__(self, replacement_lessons: list[Lesson], weekday: int, shift: int, ):
        self.replacement_lessons = replacement_lessons
        self.weekday = weekday
        self.shift = shift
        self.default_schedule: Lesson = self._get_default_schedule()
        self.default_schedule_rep = DefaultScheduleRepository()

    def _get_default_schedule(self):
        default_schedule = self.default_schedule_rep.get(self.shift,
                                                         self.weekday)
        if default_schedule is None:
            return None

        # todo: deserialize
        return default_schedule
