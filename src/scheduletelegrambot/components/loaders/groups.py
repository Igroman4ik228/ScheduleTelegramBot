from pydantic import BaseModel, ConfigDict, Field

from scheduletelegrambot.database.repositories.departments import DepartmentRepository
from scheduletelegrambot.database.repositories.groups import GroupRepository
from scheduletelegrambot.enums import StudyShift
from scheduletelegrambot.helpers.file import get_file_paths, load_from_json
from scheduletelegrambot.utils.constants import FILE_EXTENSION

from .paths import DEPARTMENTS_DIR


class InitialGroup(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1)
    study_shift: StudyShift


class InitialDepartment(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    department_name: str = Field(min_length=1)
    groups: list[InitialGroup] = Field(min_length=1)


class GroupLoader:
    def __init__(self, departments: DepartmentRepository, groups: GroupRepository) -> None:
        self.departments = departments
        self.groups = groups

    async def read(self) -> list[InitialDepartment]:
        departments = [
            InitialDepartment.model_validate(await load_from_json(str(path)))
            for path in get_file_paths(DEPARTMENTS_DIR, FILE_EXTENSION)
        ]
        if not departments:
            raise ValueError("Не найдены файлы отделений")
        group_names = [group.name for department in departments for group in department.groups]
        if len(group_names) != len(set(group_names)):
            raise ValueError("Группы в данных отделений должны быть уникальны")
        return departments

    async def load(self, departments_data: list[InitialDepartment]) -> bool:
        if await self.groups.count():
            return False
        for department_data in departments_data:
            department = await self.departments.get_by_name(department_data.department_name)
            if department is None:
                department = await self.departments.create(name=department_data.department_name)
            for group_data in department_data.groups:
                await self.groups.create(
                    name=group_data.name,
                    department_id=department.id,
                    study_shift=group_data.study_shift,
                )
        return True
