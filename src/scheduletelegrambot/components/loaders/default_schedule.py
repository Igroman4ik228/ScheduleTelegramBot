import asyncio
from pathlib import Path
from typing import TYPE_CHECKING

from scheduletelegrambot.database.db import DatabaseAlchemy, with_session
from scheduletelegrambot.database.repositories.default_schedule import DefaultScheduleRepository
from scheduletelegrambot.database.repositories.groups import GroupRepository
from scheduletelegrambot.helpers.default_schedule_parser import (
    default_schedule_parse,
)
from scheduletelegrambot.helpers.file import get_file_paths, load_from_json
from scheduletelegrambot.services.default_schedule import DefaultScheduleService
from scheduletelegrambot.utils.constants import FILE_EXTENSION

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

PATH_TEMPLATE_DATA = Path("data/schedule/")


class DefaultScheduleLoader:
    """Загружает расписание из файлов в БД."""

    def __init__(self, db: DatabaseAlchemy):
        self.db = db

    async def process_all_files(self):
        file_paths = get_file_paths(PATH_TEMPLATE_DATA, FILE_EXTENSION)
        await asyncio.gather(*(self.process_file(file_path) for file_path in file_paths))

    async def process_file(self, file_path: Path):
        group_names = file_path.stem.split("_")

        data = await load_from_json(str(file_path))
        schedule_data = default_schedule_parse(data)

        for group_name in group_names:
            await self._save_group_schedule_to_db(schedule_data, group_name)

    async def _save_group_schedule_to_db(self, schedule_data: dict, group_name: str):
        for shift, weekdays in schedule_data.items():
            for weekday, lessons in weekdays.items():
                lessons_data = str(lessons)
                await self._save_to_db(weekday, shift, lessons_data, group_name)

    @with_session
    async def _save_to_db(
        self,
        weekday: int,
        shift: int,
        data_lessons: str,
        group_name: str,
        session: AsyncSession,
    ):
        default_schedules = DefaultScheduleService(
            DefaultScheduleRepository(session), GroupRepository(session)
        )
        exist_default_schedule = await default_schedules.get_by_group_name(
            weekday, shift, group_name
        )
        if exist_default_schedule is None:
            await default_schedules.create_by_group_name(weekday, shift, data_lessons, group_name)
        else:
            if exist_default_schedule.data_lessons == data_lessons:
                return

            await default_schedules.update_lessons(exist_default_schedule, data_lessons)
