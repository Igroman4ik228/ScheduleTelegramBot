from logging import getLogger

from services.parser_service.lesson import Lesson
from services.parser_service.week import Week
from utils.constants import DAY_NAME_CASES


class ScheduleFormatter:
    def __init__(self, lessons: list[Lesson]):
        self.logger = getLogger(__name__)
        self.lessons = sorted(
            lessons,
            key=lambda lesson: lesson.number
        )

    def format_schedule(self) -> str:
        return self.format_header() + self.format_lessons()

    def format_header(self) -> str:
        weekday_name = Week().get_weekday_name()
        weekday_name = DAY_NAME_CASES.get(weekday_name, weekday_name)
        shift = Week().get_shift_name()

        return f"Расписание на <b>{weekday_name}</b> ({shift}):\n"

    def format_lessons(self) -> str:
        formatted_lessons = ""
        for lesson in self.lessons:
            formatted_lessons += self.format_lesson(lesson)

        return formatted_lessons

    def format_lesson(self, lesson: Lesson) -> str:
        formatted_lesson = f"{lesson.number}. "

        if lesson.time is not None:
            formatted_lesson += f"{lesson.time}"

        formatted_lesson += f"{lesson.subject}"

        if lesson.classroom != '':
            formatted_lesson += f" [{lesson.classroom}]"

        if lesson.is_replacement:
            formatted_lesson += " (❗️ замена)"
        formatted_lesson += "\n"

        return formatted_lesson

    @staticmethod
    def add_time_to_schedule(schedule: str) -> str:
        result_lessons: list[str] = []

        lines = schedule.split('\n')
        lessons = lines[1:]
        for lesson in lessons:
            if not lesson or not lesson[0].isdigit():
                result_lesson = lesson
                continue

            lesson_number = int(lesson[0])

            full_time = Lesson.get_full_time(lesson_number)
            result_lesson = f"{lesson} {full_time}"

            result_lessons.append(result_lesson)

        header_schedule = lines[0]
        result_lessons_str = '\n'.join(result_lessons)

        return f"{header_schedule}\n{result_lessons_str}"
