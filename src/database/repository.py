from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories.default_schedule import DefaultScheduleRepository
from database.repositories.departments import DepartmentRepository
from database.repositories.groups import GroupRepository
from database.repositories.result_schedule import ResultScheduleRepository
from database.repositories.users import UserRepository


@dataclass
class Repository:
    session: AsyncSession

    @property
    def users(self) -> UserRepository:
        return UserRepository(self.session)

    @property
    def groups(self) -> GroupRepository:
        return GroupRepository(self.session)

    @property
    def departments(self) -> DepartmentRepository:
        return DepartmentRepository(self.session)

    @property
    def result_schedule(self) -> ResultScheduleRepository:
        return ResultScheduleRepository(self.session)

    @property
    def default_schedule(self) -> DefaultScheduleRepository:
        return DefaultScheduleRepository(self.session)
