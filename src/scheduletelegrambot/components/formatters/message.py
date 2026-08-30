from scheduletelegrambot.components.formatters.schedule import format_header, format_lesson
from scheduletelegrambot.enums import WeekType
from scheduletelegrambot.helpers.lesson import Lesson, TeachingAssignment
from scheduletelegrambot.schemas.default_schedule import DefaultScheduleBaseSchema


def format_default_schedules(
    default_schedules: list[DefaultScheduleBaseSchema], week_type: WeekType
) -> str:
    return "\n".join(
        format_header(schedule.weekday, week_type, is_default_schedule=True)
        + format_default_schedule(schedule)
        for schedule in default_schedules
    )


def format_default_schedule(default_schedule: DefaultScheduleBaseSchema) -> str:
    lessons = (
        Lesson(
            number=lesson.number,
            time=None,
            subject=lesson.subject.name,
            teaching_assignments=[
                TeachingAssignment(
                    teacher=assignment.teacher.name,
                    classrooms=tuple(
                        classroom.classroom.name for classroom in assignment.classrooms
                    ),
                )
                for assignment in lesson.teaching_assignments
            ],
        )
        for lesson in sorted(default_schedule.lessons, key=lambda item: item.number)
    )
    return "".join(format_lesson(lesson) for lesson in lessons)
