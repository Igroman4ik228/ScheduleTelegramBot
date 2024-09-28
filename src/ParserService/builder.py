import json
from logging import getLogger

from database.repositories.default_schedule import DefaultScheduleRepository
from database.repositories.result_schedule import ResultScheduleRepository
from ParserService.lesson import Lesson


class Builder:

    def __init__(self, weekday: int, shift: int, ):
        self.default_schedule = {
            "ИС1-31": [Lesson(numbers=[3], time=None,
                              subject='Математика', classroom='Аудитория 1')],
            "СД2-22": [Lesson(numbers=[2, 3, 4, 5], time=None,
                              subject='Физика', classroom='Аудитория 2')],
            "ДИ1-31": [Lesson(numbers=[1, 3, 5], time=None,
                              subject='Химия', classroom='Аудитория 3')],
            "СА1-1": [Lesson(numbers=[2], time=None,
                             subject='Биология', classroom='Аудитория 4')],
        }  # for testing
        self.weekday = weekday
        self.shift = shift
        self.logger = getLogger(__name__)
        self.default_schedule_rep = DefaultScheduleRepository()
        self.result_schedule_rep = ResultScheduleRepository()

    def _get_default_schedule(self) -> dict[str, list[Lesson]]:
        default_schedule_data = self.default_schedule_rep.get(self.shift,
                                                              self.weekday)
        if default_schedule_data is None:
            return []

        return [Lesson.from_dict(lesson) for lesson in json.loads(default_schedule_data)]

    def apply_replacement(self, replacement_lessons: dict[str, list[Lesson]]) -> dict[str, list[Lesson]]:
        for group, lessons in replacement_lessons.items():
            for lesson in lessons:
                found = False
                default_lessons = self.default_schedule.get(group, [])

                for default_lesson in default_lessons:
                    if default_lesson.numbers == lesson.numbers:
                        self._update_lesson(default_lesson, lesson)
                        found = True
                        break

                    has_common_numbers = bool(
                        set(default_lesson.numbers) & set(lesson.numbers)
                    )
                    if has_common_numbers:
                        updated_numbers = (
                            set(default_lesson.numbers) - set(lesson.numbers)
                        )
                        default_lesson.numbers = list(updated_numbers)
                        self.default_schedule[group].append(lesson)
                        found = True

                if not found:
                    if group not in self.default_schedule:
                        self.default_schedule[group] = []

                    self.default_schedule[group].append(lesson)

        return self.default_schedule

    def _update_lesson(self, lesson: Lesson, replacement_lesson: Lesson):
        lesson.is_replacement = True
        lesson.time = replacement_lesson.time
        lesson.subject = replacement_lesson.subject
        lesson.classroom = replacement_lesson.classroom

    def build_result_schedule(self, result_schedule_data: dict[str, list[Lesson]]) -> dict[str, str]:
        result_schedule = {}
        for group, lessons in result_schedule_data.items():
            formatted_schedule = self.format_schedule(lessons)
            result_schedule[group] = formatted_schedule
        return result_schedule

    def format_schedule(self, result_lessons: list[Lesson]) -> str:
        for result_lesson in result_lessons:
            formatted_schedule = f"Расписание на {self.weekday} "
            formatted_schedule += f"({self.shift}):\n"

            for number in result_lesson.numbers:
                formatted_schedule += f"{number}. "

                if result_lesson.time is not None:
                    formatted_schedule += f"{result_lesson.time}"

                formatted_schedule += f"{result_lesson.subject}"

                if result_lesson.classroom != '':
                    formatted_schedule += f" [{result_lesson.classroom}]"

                if result_lesson.is_replacement:
                    formatted_schedule += " (❗️ замена)"

                formatted_schedule += "\n"
        return formatted_schedule

    async def save_schedule_to_db(self, result_schedule: dict[str, str]):
        for group, schedule in result_schedule.items():
            # todo: redis
            await self.result_schedule_rep.delete(group, self.weekday)

            self.logger.info(f"{group}")
            self.logger.info(f"{schedule}")
            await self.result_schedule_rep.create(group, self.weekday, schedule)
