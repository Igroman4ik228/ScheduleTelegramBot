from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from scheduletelegrambot.database.repositories.default_schedule import (
    DefaultScheduleRepository,
)
from scheduletelegrambot.database.repositories.departments import (
    DepartmentRepository,
)
from scheduletelegrambot.database.repositories.groups import (
    GroupRepository,
)
from scheduletelegrambot.database.repositories.referrals import (
    ReferralRepository,
)
from scheduletelegrambot.database.repositories.result_schedule import (
    ResultScheduleRepository,
)
from scheduletelegrambot.database.repositories.subscribes import (
    SubscribeRepository,
)
from scheduletelegrambot.database.repositories.users import UserRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class Repository:
    """Фабрика репозиториев для одной SQLAlchemy-сессии."""

    session: AsyncSession

    @cached_property
    def departments(self) -> DepartmentRepository:
        return DepartmentRepository(self.session)

    @cached_property
    def groups(self) -> GroupRepository:
        return GroupRepository(self.session)

    @cached_property
    def default_schedule(self) -> DefaultScheduleRepository:
        return DefaultScheduleRepository(self.session)

    @cached_property
    def subscribes(self) -> SubscribeRepository:
        return SubscribeRepository(self.session)

    @cached_property
    def referrals(self) -> ReferralRepository:
        return ReferralRepository(self.session)

    @cached_property
    def users(self) -> UserRepository:
        return UserRepository(self.session)

    @cached_property
    def result_schedule(self) -> ResultScheduleRepository:
        return ResultScheduleRepository(self.session)
