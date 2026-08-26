from __future__ import annotations

from scheduletelegrambot.database.models import DepartmentModel
from scheduletelegrambot.database.repositories.departments import DepartmentRepository


class DepartmentService:
    def __init__(self, repository: DepartmentRepository) -> None:
        self.repository = repository

    async def get_by_id(self, department_id: int) -> DepartmentModel | None:
        return await self.repository.get_by_id(department_id)

    async def get_by_name(self, name: str) -> DepartmentModel | None:
        return await self.repository.get_one(DepartmentModel.name == name)

    async def get_all(self) -> list[DepartmentModel]:
        return await self.repository.get_many()
