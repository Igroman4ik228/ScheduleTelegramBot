import json
from logging import getLogger
from pathlib import Path

from database.db import sessionmaker
from database.models.default_schedule import DefaultScheduleModel
from database.models.groups import GroupModel
from database.repositories.users import GroupRepository


class ScheduleLoader:
    def __init__(self):
        self.logger = getLogger(__name__)

    def _open_file(self, file_name: str):
        with open(file_name, 'r', encoding="UTF-8") as f:
            return json.load(f)

    def _get_all_files(self) -> list[Path]:
        directory = Path("src/services/loader_service/data")

        return [file for file in directory.iterdir() if file.is_file()]

    async def _get_group_id(self, group_name: str):
        async with sessionmaker() as session:
            group = await GroupRepository(session).get_by_name(group_name)
        return group.id

    async def loading(self):
        # File
        for file in self._get_all_files():
            data = self._open_file(file.resolve())
            self.logger.info(f"Start for {file}")
            print(f"Start for {file}")
            group_id = await self._get_group_id((file.name).split(".")[0])

            schedule_models = []

            # Type of week (1 и 2)
            for shift, shift_data in data.items():
                # Weekday (0 до 5)
                for weekday, weekday_data in shift_data.items():
                    schedule_model = DefaultScheduleModel(
                        weekday=weekday,
                        shift=int(shift),
                        data_lessons="",
                        group_id=group_id
                    )

                    lessons_list = []

                    # Lessons
                    for lesson in weekday_data:
                        lessons_list.append(lesson)

                    # List to Json
                    schedule_model.data_lessons = json.dumps(
                        lessons_list, ensure_ascii=False
                    )
                    schedule_models.append(schedule_model)

            # Debug print
            for model in schedule_models:
                self.logger.info(f"Default Schedule Information:\n  Weekday: {model.weekday}\n  Shift: {
                                 model.shift}\n  Data Lessons: {model.data_lessons}\n  Group ID: {model.group_id}\n")

    async def _save_to_db(self):
        ...
