import asyncio
from pathlib import Path

from database.db import with_session_self
from database.repositories.default_schedule import DefaultScheduleRepository
from helpers.file import get_file_paths, load_from_json
from utils.constants import PATH_TEMPLATE_DATA


class DefaultScheduleLoader:
    async def process_all_files(self):
        file_paths = get_file_paths(PATH_TEMPLATE_DATA, "json")
        await asyncio.gather(*(self.process_file(file_path) for file_path in file_paths))

    async def process_file(self, file_path: str):
        group_names = Path(file_path).stem.split("_")

        data = await load_from_json(file_path)
        schedule_data = DefaultScheduleParser.parse(data)

        for group_name in group_names:
            await self._process_group_schedule(schedule_data, group_name)

    async def _process_group_schedule(self, schedule_data: dict, group_name: str):
        for shift, weekdays in schedule_data.items():
            for weekday, lessons in weekdays.items():
                lessons_data = str(lessons)
                await self._save_to_db(weekday, shift, lessons_data, group_name)

    @with_session_self
    async def _save_to_db(
        self,
        session,
        weekday: int,
        shift: int,
        data_lessons: str,
        group_name: str
    ):
        repo = DefaultScheduleRepository(session)
        exist_default_schedule = await repo.get_by_group_name(
            weekday, shift, group_name
        )
        if exist_default_schedule is None:
            await repo.create_by_group_name(
                weekday,
                shift,
                data_lessons,
                group_name
            )
        else:
            await repo.delete(
                weekday, shift, exist_default_schedule.group_id
            )
            await repo.create(
                weekday, shift, data_lessons, exist_default_schedule.group_id
            )


class DefaultScheduleParser:
    @staticmethod
    def parse(data: dict[str, any]) -> dict:
        schedule_data = {}
        for shift_str, weekdays in data.items():
            shift = int(shift_str)
            schedule_data[shift] = {}

            for weekday_str, lessons in weekdays.items():
                weekday = int(weekday_str)
                schedule_data[shift][weekday] = list(lessons)

        return schedule_data
