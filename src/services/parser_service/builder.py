from logging import getLogger

from database.db import with_session_self
from database.models.groups import GroupModel
from database.repository import Repository
from helpers.default_schedule_parser import get_default_lessons
from helpers.lesson import Lesson, Schedule
from helpers.week import Week
from services.formatter_service.schedule import format_schedule


class Builder:

    def __init__(self, replacement_schedules: list[Schedule]):
        self.logger = getLogger(__name__)
        self.replacement_schedules = replacement_schedules
        self.default_schedules: list[Schedule] = []

    async def main_build(self) -> dict[str, str]:
        """
        Return:
            dict[str, str]: A dictionary with group names as keys and formatted schedules as values
        """
        self.default_schedule = await self._get_default_schedules()
        result_schedules_data = self._apply_replacement()

        result_schedule = {}
        for schedule in result_schedules_data:
            formatted_schedule = format_schedule(
                schedule.lessons, Week().weekday, Week().shift
            )
            result_schedule[schedule.group] = formatted_schedule

        return result_schedule

    @with_session_self
    async def _get_default_schedules(self, session) -> list[Schedule]:
        default_schedule_rep = Repository(session).default_schedule
        default_schedule_data = await default_schedule_rep.get_all(weekday=Week().weekday,
                                                                   shift=Week().shift)

        if default_schedule_data is None:
            return []

        default_schedule: list[Schedule] = []
        for default_lesson in default_schedule_data:
            default_lesson_group: GroupModel = default_lesson.group

            default_lessons = get_default_lessons(default_lesson.data_lessons)
            for default_schedule_lesson in default_lessons:
                default_schedule.append(
                    Schedule(
                        week=Week(),
                        group=default_lesson_group.name,
                        lessons=[default_schedule_lesson]
                    )
                )
        return default_schedule

    def _apply_replacement(self) -> list[Schedule]:
        for replacement_schedule in self.replacement_schedules:
            for replacement_lesson in replacement_schedule.lessons:
                is_found = False
                for default_schedule in self.default_schedules:
                    for default_lesson in default_schedule.lessons:
                        if default_lesson.number == replacement_lesson.number:
                            self._update_lesson(
                                default_lesson, replacement_lesson)
                            is_found = True
                            break

                # if not found number
                if not is_found:
                    for default_schedule in self.default_schedules:
                        if default_schedule.group == replacement_schedule.group:
                            default_schedule.lessons.append(replacement_lesson)

        return self.default_schedule

    def _update_lesson(self, lesson: Lesson, replacement_lesson: Lesson):
        lesson.is_replacement = True
        lesson.time = replacement_lesson.time
        lesson.subject = replacement_lesson.subject
        lesson.classroom = replacement_lesson.classroom
