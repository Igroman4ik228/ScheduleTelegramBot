from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from database.cache.repositories import CacheRepositoryService
from database.repositories import (
    DefaultScheduleRepository,
    DepartmentRepository,
    GroupRepository,
    ReferralRepository,
    ResultScheduleRepository,
    SubscribeRepository,
    UserRepository,
)


@dataclass
class Repository:
    """Фабрика для репозиториев"""

    session: AsyncSession

    @property
    def groups(self) -> GroupRepository:
        return GroupRepository(self.session)

    @property
    def departments(self) -> DepartmentRepository:
        return DepartmentRepository(self.session)

    @property
    def default_schedule(self) -> DefaultScheduleRepository:
        return DefaultScheduleRepository(self.session)

    @property
    def subscribes(self) -> SubscribeRepository:
        return SubscribeRepository(self.session)

    @property
    def referrals(self) -> ReferralRepository:
        return ReferralRepository(self.session)


@dataclass
class CachedRepository(Repository):
    """Фабрика для репозиториев, включающая репозитории с кэшом"""

    cache_service: CacheRepositoryService

    @property
    def users(self) -> UserRepository:
        return UserRepository(self.session, self.cache_service)

    @property
    def result_schedule(self) -> ResultScheduleRepository:
        return ResultScheduleRepository(self.session, self.cache_service)
