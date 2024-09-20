import json

from database.repositories.default_schedule import DefaultScheduleRepository
from database.repositories.result_schedule import ResultScheduleRepository
from ParserService.lesson import Lesson


class Builder():

    def __init__(self, replacement_lessons: list[Lesson], weekday: int, shift: int, ):
        self.replacement_lessons = replacement_lessons
        self.default_lessons = {
            "ИС1-31": [Lesson(group='ИС1-31', numbers=[3], time=None,
                              subject='Математика', classroom='Аудитория 1')],
            "СД2-22": [Lesson(group='СД2-22', numbers=[2, 3, 4, 5], time=None,
                              subject='Физика', classroom='Аудитория 2')],
            "ДИ1-31": [Lesson(group='ДИ1-31', numbers=[1, 3, 5], time=None,
                              subject='Химия', classroom='Аудитория 3')],
            "СА1-1": [Lesson(group='СА1-1', numbers=[2], time=None,
                             subject='Биология', classroom='Аудитория 4')],
        }
        self.weekday = weekday
        self.shift = shift
        self.default_schedule_rep = DefaultScheduleRepository()
        self.result_schedule_rep = ResultScheduleRepository()

    def _get_default_schedule(self) -> dict[str, list[Lesson]]:
        default_schedule_data = self.default_schedule_rep.get(self.shift,
                                                              self.weekday)
        if default_schedule_data is None:
            return []

        return [Lesson.from_dict(lesson) for lesson in json.loads(default_schedule_data)]

    @ staticmethod
    def grouping_schedule(lessons: list[Lesson]) -> dict[str, list[Lesson]]:
        group_lessons: dict[str, list[Lesson]] = {}
        for lesson in lessons:

            if lesson.group not in group_lessons:
                group_lessons[lesson.group] = [lesson]
            else:
                group_lessons[lesson.group].append(lesson)

        return group_lessons

    def apply_replacement(self,
                          replacement_lessons: dict[str, list[Lesson]]) -> dict[str, list[Lesson]]:
        default_schedule = self.default_lessons
        pass

    def format_schedule(self, result_schedule: list[Lesson]) -> dict[str, str]:
        formatted_group_data = {}
        for result_lesson in result_schedule:
            formatted_schedule = f"Расписание на {self.weekday}({self.shift}):"
            for number in result_lesson.numbers:
                formatted_schedule += f"{number}. {result_lesson.time} "
                formatted_schedule += f"{result_lesson.subject} "
                formatted_schedule += f"[{result_lesson.classroom}]"

                if result_lesson.is_replacement:
                    formatted_schedule += "(❗️ замена)"

                formatted_schedule += "\n"
            formatted_group_data[result_lesson.group] = formatted_schedule

    def save_schedule_to_db(self, result_schedule: dict[str, str]):
        pass
