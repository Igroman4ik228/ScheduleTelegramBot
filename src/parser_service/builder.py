import json
from logging import getLogger

from database.db import with_session_self
from database.redis.base import create_redis
from database.redis.schedule_cache import ScheduleCache
from database.repositories.result_schedule import ResultScheduleRepository
from parser_service.lesson import Lesson
from parser_service.week import Week
from utils.constants import DAY_NAME_CASES


class Builder:

    def __init__(self, weekday: int, shift: int, ):
        self.logger = getLogger(__name__)
        self.schedule_cache = ScheduleCache(create_redis())
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
        self.weekday = weekday
        self.shift = shift

    async def _get_default_schedule(self) -> dict[str, list[Lesson]]:
        # async with sessionmaker() as session:
        #     default_schedule_data = await DefaultScheduleRepository(session).get(self.shift,
        #                                                                          self.weekday)
        default_schedule_data = None
        if default_schedule_data is None:
            return []

        return [Lesson.from_dict(lesson) for lesson in json.loads(default_schedule_data)]

    def apply_replacement(
        self, replacement_lessons: dict[str, list[Lesson]]
    ) -> dict[str, list[Lesson]]:
        for group, lessons in replacement_lessons.items():
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

    def build_result_schedule(
        self, result_schedule_data: dict[str, list[Lesson]]
    ) -> dict[str, str]:
        result_schedule = {}
        for group, lessons in result_schedule_data.items():
            formatted_schedule = self.format_schedule(lessons)
            result_schedule[group] = formatted_schedule
        return result_schedule

    def format_schedule(self, result_lessons: list[Lesson]) -> str:
        weekday_name = Week.get_weekday_name(self.weekday)
        weekday_name = DAY_NAME_CASES.get(weekday_name, weekday_name)
        formatted_schedule = f"Расписание на {weekday_name} "

        shift_name = Week.get_shift_name(self.shift)
        formatted_schedule += f"({shift_name}):\n"

        result_lessons.sort(key=lambda lesson: lesson.number)
        for result_lesson in result_lessons:
            formatted_schedule += f"{result_lesson.number}. "

            if result_lesson.time is not None:
                formatted_schedule += f"{result_lesson.time}"

            formatted_schedule += f"{result_lesson.subject}"

            if result_lesson.classroom != '':
                formatted_schedule += f" [{result_lesson.classroom}]"

            if result_lesson.is_replacement:
                formatted_schedule += " (❗️ замена)"

            formatted_schedule += "\n"
        return formatted_schedule

    @with_session_self
    async def save_schedule_to_db(self, session, result_schedule: dict[str, str]):
        result_schedule_rep = ResultScheduleRepository(session)
        for group, schedule in result_schedule.items():
            self.schedule_cache.create(self.weekday, group, schedule)

            await result_schedule_rep.delete_by_group_name(self.weekday, group)

            await result_schedule_rep.create_by_group_name(self.weekday, schedule, group)
