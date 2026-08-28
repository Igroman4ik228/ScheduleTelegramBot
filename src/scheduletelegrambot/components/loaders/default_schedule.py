from pathlib import Path

from scheduletelegrambot.helpers.default_schedule_parser import default_schedule_parse
from scheduletelegrambot.helpers.file import get_file_paths, load_from_json
from scheduletelegrambot.schemas.default_schedule import (
    DefaultScheduleCreateSchema,
    DefaultScheduleUpdateSchema,
)
from scheduletelegrambot.services.default_schedule import DefaultScheduleService
from scheduletelegrambot.utils.constants import FILE_EXTENSION

from .paths import SCHEDULES_DIR


class DefaultScheduleLoader:
    def __init__(self, default_schedules: DefaultScheduleService) -> None:
        self.default_schedules = default_schedules

    async def load(self) -> None:
        file_paths = get_file_paths(SCHEDULES_DIR, FILE_EXTENSION)
        for file_path in file_paths:
            await self._load_file(file_path)

    async def _load_file(self, file_path: Path) -> None:
        group_names = file_path.stem.split("_")
        data = await load_from_json(str(file_path))
        schedule_data = default_schedule_parse(data)

        for group_name in group_names:
            await self._load_group_schedule(schedule_data, group_name)

    async def _load_group_schedule(self, schedule_data: dict, group_name: str) -> None:
        for shift, weekdays in schedule_data.items():
            for weekday, lessons in weekdays.items():
                await self._save_schedule(
                    weekday,
                    shift,
                    str(lessons),
                    group_name,
                )

    async def _save_schedule(
        self,
        weekday: int,
        shift: int,
        data_lessons: str,
        group_name: str,
    ) -> None:
        schedule = await self.default_schedules.find_for_group_name(
            weekday,
            shift,
            group_name,
        )
        if schedule is None:
            await self.default_schedules.create_for_group(
                DefaultScheduleCreateSchema(
                    weekday=weekday,
                    shift=shift,
                    data_lessons=data_lessons,
                    group_name=group_name,
                )
            )
            return

        if schedule.data_lessons != data_lessons:
            await self.default_schedules.update_lessons(
                DefaultScheduleUpdateSchema(id=schedule.id, data_lessons=data_lessons)
            )
