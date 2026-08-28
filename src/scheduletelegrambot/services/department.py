from __future__ import annotations

from cashews import NOT_NONE, noself

from scheduletelegrambot.cache.cashews import cache
from scheduletelegrambot.database.repositories.departments import DepartmentRepository
from scheduletelegrambot.database.uow import UoW
from scheduletelegrambot.schemas.department import DepartmentBaseSchema

_CACHE_TAG = "departments"


class DepartmentService:
    def __init__(self, department_repository: DepartmentRepository, uow: UoW) -> None:
        self.department_repository = department_repository
        self.uow = uow

    @noself(cache.early)(
        ttl="24h",
        early_ttl="12h",
        tags=(_CACHE_TAG,),
        condition=NOT_NONE,
    )
    async def find_by_id(self, department_id: int) -> DepartmentBaseSchema | None:
        model = await self.department_repository.get_by_id(department_id)
        if not model:
            return None

        return DepartmentBaseSchema.model_validate(model)

    @noself(cache.early)(
        ttl="24h",
        early_ttl="12h",
        tags=(_CACHE_TAG,),
        condition=NOT_NONE,
    )
    async def find_by_name(self, name: str) -> DepartmentBaseSchema | None:
        model = await self.department_repository.get_by_name(name)
        if not model:
            return None

        return DepartmentBaseSchema.model_validate(model)

    @noself(cache.early)(
        ttl="24h",
        early_ttl="12h",
        tags=(_CACHE_TAG,),
    )
    async def list_all(self) -> list[DepartmentBaseSchema]:
        models = await self.department_repository.list_all()
        return [DepartmentBaseSchema.model_validate(model) for model in models]
