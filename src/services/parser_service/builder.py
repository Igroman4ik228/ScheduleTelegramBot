from logging import getLogger

from database.db import sessionmaker
from database.repository import Repository
from services.parser_service.formatter import ScheduleFormatter
from services.parser_service.lesson import Lesson


class Builder:

    def __init__(self, replacement_schedule: dict[str, list[Lesson]]):
        self.logger = getLogger(__name__)
        self.replacement_schedule = replacement_schedule
        self.default_schedule = {
            "ИС1-43": [Lesson(number=0, time=None,
                              subject='Математика', classroom='Аудитория 1')],
            "ИБ1-41": [Lesson(number=3, time=None,
                              subject='Математика', classroom='Аудитория 1')],
            "ИС1-31": [Lesson(number=3, time=None,
                              subject='Математика', classroom='Аудитория 1')],
            "СД2-22": [Lesson(number=2, time=None,
                              subject='Физика', classroom='Аудитория 2')],
            "ДИ1-31": [Lesson(number=1, time=None,
                              subject='Химия', classroom='Аудитория 3')],
            "СА1-1": [Lesson(number=2, time=None,
                             subject='Биология', classroom='Аудитория 4')],
        }  # for testing

    def main_build(self) -> dict[str, str]:
        result_schedule_data = self._apply_replacement()
        result_schedule = {}
        for group, lessons in result_schedule_data.items():
            schedule_formatter = ScheduleFormatter(lessons)
            formatted_schedule = schedule_formatter.format_schedule()
            result_schedule[group] = formatted_schedule

        return result_schedule

    # TODO: finish it later
    async def _get_default_schedule(self) -> dict[str, list[Lesson]]:
        async with sessionmaker() as session:
            default_schedule_rep = Repository(session).default_schedule
            default_schedule_data = await default_schedule_rep.get_all()

        if default_schedule_data is None:
            return []

        return []

    def _apply_replacement(self) -> dict[str, list[Lesson]]:
        for group, lessons in self.replacement_schedule.items():
            for lesson in lessons:
                is_found = False
                default_lessons = self.default_schedule.get(group, [])

                for default_lesson in default_lessons:
                    if default_lesson.number == lesson.number:
                        self._update_lesson(default_lesson, lesson)
                        is_found = True
                        break

                if not is_found:
                    if group not in self.default_schedule:
                        self.default_schedule[group] = []
                    self.default_schedule[group].append(lesson)

        return self.default_schedule

    def _update_lesson(self, lesson: Lesson, replacement_lesson: Lesson):
        lesson.is_replacement = True
        lesson.time = replacement_lesson.time
        lesson.subject = replacement_lesson.subject
        lesson.classroom = replacement_lesson.classroom
