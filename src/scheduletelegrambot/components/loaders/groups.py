from pydantic import BaseModel, Field

from scheduletelegrambot.database.repositories.departments import DepartmentRepository
from scheduletelegrambot.database.repositories.groups import GroupRepository
from scheduletelegrambot.database.uow import UoW
from scheduletelegrambot.helpers.file import load_from_json

from .paths import GROUPS_FILE_PATH


class InitialGroup(BaseModel):
    name: str
    global_shift: int = Field(default=1, ge=1)


class InitialDepartment(BaseModel):
    name: str
    groups: list[InitialGroup]


class InitialGroupsData(BaseModel):
    departments: list[InitialDepartment]


class GroupLoader:
    def __init__(
        self,
        departments: DepartmentRepository,
        groups: GroupRepository,
        uow: UoW,
    ) -> None:
        self.departments = departments
        self.groups = groups
        self.uow = uow

    async def load(self) -> None:
        data = InitialGroupsData.model_validate(await load_from_json(str(GROUPS_FILE_PATH)))
        is_changed = False

        for department_data in data.departments:
            department = await self.departments.get_by_name(department_data.name)
            if department is None:
                department = await self.departments.create(name=department_data.name)
                is_changed = True

            for group_data in department_data.groups:
                group = await self.groups.get_by_name(group_data.name)
                if group is not None:
                    continue

                await self.groups.create(
                    name=group_data.name,
                    department_id=department.id,
                    global_shift=group_data.global_shift,
                )
                is_changed = True

        if is_changed:
            await self.uow.commit()
