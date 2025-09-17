from dataclasses import dataclass
from functools import cached_property

from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories import (
    DefaultScheduleRepository,
    DepartmentRepository,
    GroupRepository,
    ReferralRepository,
    ResultScheduleRepository,
    SubscribeRepository,
)
from database.repositories.users_copy import UserRepository
from helpers.cache import CacheHelper


@dataclass
class Repository:
    """Фабрика для репозиториев"""

    session: AsyncSession

    @cached_property
    def groups(self) -> GroupRepository:
        return GroupRepository(self.session)

    @cached_property
    def departments(self) -> DepartmentRepository:
        return DepartmentRepository(self.session)

    @cached_property
    def default_schedule(self) -> DefaultScheduleRepository:
        return DefaultScheduleRepository(self.session)

    @cached_property
    def subscribes(self) -> SubscribeRepository:
        return SubscribeRepository(self.session)

    @cached_property
    def referrals(self) -> ReferralRepository:
        return ReferralRepository(self.session)


@dataclass
class CachedRepository(Repository):
    """Фабрика для репозиториев, включающая репозитории с кэшом"""

    cache_helper: CacheHelper

    @cached_property
    def users(self) -> UserRepository:
        return UserRepository(self.session, self.cache_helper)

    @cached_property
    def result_schedule(self) -> ResultScheduleRepository:
        return ResultScheduleRepository(self.session, self.cache_helper)
