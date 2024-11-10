from logging import getLogger

from database.db import with_session_self
from database.models.groups import GroupModel
from database.repository import Repository
from helpers.generator import generate_default_schedule
from helpers.lesson import Lesson
from services.formatter_service.schedule import format_schedule
from services.parser_service.week import Week


class Builder:

    def __init__(self, replacement_schedule: dict[str, list[Lesson]]):
        self.logger = getLogger(__name__)
        self.replacement_schedule = replacement_schedule
        self.default_schedule = {}

    async def main_build(self) -> dict[str, str]:
        self.default_schedule = await self._get_default_schedule()
        result_schedule_data = self._apply_replacement()
        result_schedule = {}
        for group, lessons in result_schedule_data.items():
            formatted_schedule = format_schedule(
                lessons, Week().weekday, Week().shift
            )
            result_schedule[group] = formatted_schedule

        return result_schedule

    @with_session_self
    async def _get_default_schedule(self, session) -> dict[str, list[Lesson]]:
        default_schedule_rep = Repository(session).default_schedule
        default_schedule_data = await default_schedule_rep.get_all(weekday=Week().weekday,
                                                                   shift=Week().shift)

        if default_schedule_data is None:
            return []

        default_schedule = {}
        for default_lesson in default_schedule_data:
            default_lesson_group: GroupModel = default_lesson.group
            for default_schedule_lesson in generate_default_schedule(default_lesson.data_lessons):
                default_schedule.setdefault(
                    default_lesson_group.name, []
                ).append(default_schedule_lesson)

        return default_schedule

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
