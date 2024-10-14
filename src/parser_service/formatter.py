class ScheduleFormatter:
    def __init__(self, result_schedule: list[Lesson]):
        self.logger = getLogger(__name__)
        self.result_schedule = sorted(
            result_schedule,
            key=lambda lesson: lesson.number
        )

    def format_schedule(self) -> str:
        return self.format_header() + self.format_lessons()

    def format_header(self) -> str:
        formatted_schedule = "Расписание на "
        weekday_name = Week.get_weekday_name()
        weekday_name = DAY_NAME_CASES.get(Week.weekday, weekday_name)
        formatted_schedule += f"{weekday_name} "

        shift = Week.get_shift_name()
        formatted_schedule += f"({shift}):"
        formatted_schedule += "\n"

        return formatted_schedule

    def format_lessons(self) -> str:
        formatted_lessons = ""
        for lesson in self.result_schedule:
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
        for lesson in schedule.split('\n')[1:]:
            if lesson == '':
                continue
            lesson_number = lesson[0]
            start_time = START_LESSONS_TIME[lesson_number]
            end_time = END_LESSONS_TIME[lesson_number]
            time = f"{start_time} - {end_time}"

            lesson += f"{time}"

        return schedule
