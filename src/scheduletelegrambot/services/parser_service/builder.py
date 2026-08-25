from dataclasses import dataclass
from logging import getLogger
from typing import TYPE_CHECKING

from scheduletelegrambot.database.db import DatabaseAlchemy, with_session
from scheduletelegrambot.database.models import DefaultScheduleModel, GroupModel
from scheduletelegrambot.database.repository import Repository
from scheduletelegrambot.helpers.default_schedule_parser import (
    get_default_lessons,
)
from scheduletelegrambot.helpers.lesson import Lesson, Schedule
from scheduletelegrambot.services.formatter_service.schedule import (
    format_schedule,
)

if TYPE_CHECKING:
    from scheduletelegrambot.helpers.week import Week


@dataclass
class ScheduleBuilder:
    """Класс для построения расписания с учетом замен"""

    week: Week
    default_schedules: list[Schedule]
    replacement_schedules: list[Schedule]

    def build(self) -> dict[str, str]:
        """Построить итоговое расписание с учетом замен"""
        merged_schedules = self._merge_schedules()
        return self._format_schedules(merged_schedules)

    def _merge_schedules(self) -> list[Schedule]:
        """Объединить основное расписание с заменами"""
        schedule_merger = ScheduleMerger(
            self.week, self.default_schedules, self.replacement_schedules
        )
        return schedule_merger.merge()

    def _format_schedules(self, schedules: list[Schedule]) -> dict[str, str]:
        """Форматировать расписания для вывода"""
        return {
            schedule.group: format_schedule(schedule.lessons, self.week.weekday, self.week.shift)
            for schedule in schedules
        }


class ScheduleMerger:
    """Класс для объединения основного расписания с заменами"""

    def __init__(
        self,
        week: Week,
        default_schedules: list[Schedule],
        replacement_schedules: list[Schedule],
    ):
        self.week = week
        self.default_schedules = default_schedules
        self.replacement_schedules = replacement_schedules
        self.schedules_by_group = {schedule.group: schedule for schedule in default_schedules}

    def merge(self) -> list[Schedule]:
        """Объединить расписания, применяя замены"""
        for replacement_schedule in self.replacement_schedules:
            self._process_replacement_schedule(replacement_schedule)
        return list(self.schedules_by_group.values())

    def _process_replacement_schedule(self, replacement_schedule: Schedule) -> None:
        """Обработать расписание с заменами"""
        group_schedule = self._get_or_create_group_schedule(replacement_schedule.group)
        lesson_merger = LessonMerger(group_schedule)

        for replacement_lesson in replacement_schedule.lessons:
            lesson_merger.merge_lesson(replacement_lesson)

    def _get_or_create_group_schedule(self, group: str) -> Schedule:
        """Получить или создать расписание для группы"""
        if group not in self.schedules_by_group:
            new_schedule = Schedule(week=self.week, group=group, lessons=[])
            self.schedules_by_group[group] = new_schedule
        return self.schedules_by_group[group]


class LessonMerger:
    """Класс для объединения уроков с заменами"""

    def __init__(self, schedule: Schedule):
        self.schedule = schedule
        self.lessons_by_number = {lesson.number: lesson for lesson in schedule.lessons}

    def merge_lesson(self, replacement_lesson: Lesson) -> None:
        """Объединить урок с заменой"""
        if replacement_lesson.number in self.lessons_by_number:
            self._update_existing_lesson(replacement_lesson)
        else:
            self._add_new_lesson(replacement_lesson)

    def _update_existing_lesson(self, replacement_lesson: Lesson) -> None:
        """Обновить существующий урок"""
        existing_lesson = self.lessons_by_number[replacement_lesson.number]
        existing_lesson.is_replacement = True
        existing_lesson.time = replacement_lesson.time
        existing_lesson.subject = replacement_lesson.subject
        existing_lesson.classroom = replacement_lesson.classroom

    def _add_new_lesson(self, lesson: Lesson) -> None:
        """Добавить новый урок"""
        self.schedule.lessons.append(lesson)
        self.lessons_by_number[lesson.number] = lesson


class Builder:
    """Основной класс для построения расписания"""

    def __init__(
        self,
        db: DatabaseAlchemy,
        week: Week,
        global_shift,
        replacement_schedules: list[Schedule],
    ):
        self.logger = getLogger(self.__class__.__name__)
        self.db = db
        self.week = week
        self.global_shift = global_shift
        self.replacement_schedules = replacement_schedules
        self.default_schedules: list[Schedule] = []

    @with_session
    async def initialize(self, session=None) -> None:
        """Инициализация билдера - загрузка основного расписания"""
        self.default_schedules = await self._get_default_schedules(session)

    async def build(self) -> dict[str, str]:
        """
        Построить итоговое расписание с учетом замен

        Returns:
            Dict[str, str]: Словарь с названиями групп и отформатированными расписаниями
        """
        builder = ScheduleBuilder(
            week=self.week,
            default_schedules=self.default_schedules,
            replacement_schedules=self.replacement_schedules,
        )
        return builder.build()

    async def _get_default_schedules(self, session) -> list[Schedule]:
        """Получить основное расписание из БД"""
        default_schedule_rep = Repository(session).default_schedule

        groups = await Repository(session).groups.get_many(
            GroupModel.global_shift == self.global_shift
        )
        group_ids = {group.id for group in groups}

        default_schedule_data = await default_schedule_rep.get_many(
            DefaultScheduleModel.weekday == self.week.weekday,
            DefaultScheduleModel.shift == self.week.shift,
            options=(DefaultScheduleModel.group,),
        )

        if default_schedule_data is None:
            return []

        filtered_schedule_data = [
            schedule for schedule in default_schedule_data if schedule.group_id in group_ids
        ]

        schedule_collector = DefaultScheduleCollector(self.week)
        return schedule_collector.collect_schedules(filtered_schedule_data)


class DefaultScheduleCollector:
    """Класс для сбора основного расписания"""

    def __init__(self, week: Week):
        self.week = week
        self.schedules_by_group: dict[str, Schedule] = {}

    def collect_schedules(self, schedule_data: list[DefaultScheduleModel]) -> list[Schedule]:
        """Собрать расписания из данных БД"""
        for lesson_data in schedule_data:
            self._process_lesson_data(lesson_data)
        return list(self.schedules_by_group.values())

    def _process_lesson_data(self, lesson_data) -> None:
        """Обработать данные урока"""
        group_name = lesson_data.group.name
        lessons = get_default_lessons(lesson_data.data_lessons)

        if group_name not in self.schedules_by_group:
            self.schedules_by_group[group_name] = Schedule(
                week=self.week, group=group_name, lessons=[]
            )

        self.schedules_by_group[group_name].lessons.extend(lessons)
