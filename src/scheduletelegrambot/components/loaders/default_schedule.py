import asyncio
from pathlib import Path

from dishka import AsyncContainer

from scheduletelegrambot.helpers.default_schedule_parser import (
    default_schedule_parse,
)
from scheduletelegrambot.helpers.file import get_file_paths, load_from_json
from scheduletelegrambot.schemas.default_schedule import (
    DefaultScheduleCreateSchema,
    DefaultScheduleUpdateSchema,
)
from scheduletelegrambot.services.default_schedule import DefaultScheduleService
from scheduletelegrambot.utils.constants import FILE_EXTENSION

PATH_TEMPLATE_DATA = Path("data/schedule/")


class DefaultScheduleLoader:
    """Загружает расписание из файлов в БД."""

    def __init__(self, container: AsyncContainer) -> None:
        self.container = container

    async def process_all_files(self) -> None:
        file_paths = get_file_paths(PATH_TEMPLATE_DATA, FILE_EXTENSION)
        await asyncio.gather(*(self.process_file(file_path) for file_path in file_paths))

    async def process_file(self, file_path: Path) -> None:
        group_names = file_path.stem.split("_")

        data = await load_from_json(str(file_path))
        schedule_data = default_schedule_parse(data)

        async with self.container() as request_container:
            default_schedules = await request_container.get(DefaultScheduleService)
            for group_name in group_names:
                await self._save_group_schedule_to_db(schedule_data, group_name, default_schedules)

    async def _save_group_schedule_to_db(
        self,
        schedule_data: dict,
        group_name: str,
        default_schedules: DefaultScheduleService,
    ) -> None:
        for shift, weekdays in schedule_data.items():
            for weekday, lessons in weekdays.items():
                lessons_data = str(lessons)
                await self._save_to_db(weekday, shift, lessons_data, group_name, default_schedules)

    async def _save_to_db(
        self,
        weekday: int,
        shift: int,
        data_lessons: str,
        group_name: str,
        default_schedules: DefaultScheduleService,
    ) -> None:
        exist_default_schedule = await default_schedules.find_for_group_name(
            weekday, shift, group_name
        )
        if exist_default_schedule is None:
            await default_schedules.create_for_group(
                DefaultScheduleCreateSchema(
                    weekday=weekday,
                    shift=shift,
                    data_lessons=data_lessons,
                    group_name=group_name,
                )
            )
        else:
            if exist_default_schedule.data_lessons == data_lessons:
                return

            await default_schedules.execute_update_lessons(
                DefaultScheduleUpdateSchema(
                    id=exist_default_schedule.id, data_lessons=data_lessons
                )
            )
