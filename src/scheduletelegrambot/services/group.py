from __future__ import annotations

from cashews import NOT_NONE, noself

from scheduletelegrambot.cache.cashews import cache
from scheduletelegrambot.database.repositories.groups import GroupRepository
from scheduletelegrambot.database.uow import UoW
from scheduletelegrambot.enums import StudyShift
from scheduletelegrambot.schemas.group import GroupBaseSchema

_CACHE_TAG = "groups"


class GroupService:
    def __init__(self, group_repository: GroupRepository, uow: UoW) -> None:
        self.group_repository = group_repository
        self.uow = uow

    @noself(cache.early)(
        ttl="24h",
        early_ttl="12h",
        tags=(_CACHE_TAG,),
        condition=NOT_NONE,
    )
    async def find_by_id(self, group_id: int) -> GroupBaseSchema | None:
        model = await self.group_repository.get_by_id(group_id)
        if not model:
            return None

        return GroupBaseSchema.model_validate(model)

    @noself(cache.early)(
        ttl="24h",
        early_ttl="12h",
        tags=(_CACHE_TAG,),
        condition=NOT_NONE,
    )
    async def find_by_name(self, name: str) -> GroupBaseSchema | None:
        model = await self.group_repository.get_by_name(name)
        if not model:
            return None

        return GroupBaseSchema.model_validate(model)

    @noself(cache.early)(
        ttl="24h",
        early_ttl="12h",
        tags=(_CACHE_TAG,),
    )
    async def list_all(self) -> list[GroupBaseSchema]:
        models = await self.group_repository.list_all()
        return [GroupBaseSchema.model_validate(model) for model in models]

    @noself(cache.early)(
        ttl="24h",
        early_ttl="12h",
        tags=(_CACHE_TAG,),
    )
    async def list_all_by_department(self, department_id: int) -> list[GroupBaseSchema]:
        models = await self.group_repository.list_by_department(department_id)
        return [GroupBaseSchema.model_validate(model) for model in models]

    @noself(cache.early)(
        ttl="24h",
        early_ttl="12h",
        tags=(_CACHE_TAG,),
    )
    async def list_all_by_study_shift(self, study_shift: StudyShift) -> list[GroupBaseSchema]:
        models = await self.group_repository.list_by_study_shift(study_shift)
        return [GroupBaseSchema.model_validate(model) for model in models]

    async def delete_by_name(self, name: str) -> bool:
        result = await self.group_repository.execute_delete_by_name(name)
        deleted = result.rowcount > 0

        if deleted:
            await self.uow.commit()
            await cache.delete_tags(_CACHE_TAG)

        return deleted
