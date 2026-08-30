from scheduletelegrambot.cache.cashews import cache
from scheduletelegrambot.components.loaders.default_schedule import DefaultScheduleLoader
from scheduletelegrambot.components.loaders.groups import GroupLoader
from scheduletelegrambot.components.loaders.subscriptions import SubscribeLoader
from scheduletelegrambot.database.uow import UoW


class InitialDataLoader:
    def __init__(
        self,
        group_loader: GroupLoader,
        subscribe_loader: SubscribeLoader,
        default_schedule_loader: DefaultScheduleLoader,
        uow: UoW,
    ) -> None:
        self.group_loader = group_loader
        self.subscribe_loader = subscribe_loader
        self.default_schedule_loader = default_schedule_loader
        self.uow = uow

    async def load(self) -> None:
        async with self.uow.begin():
            await self.default_schedule_loader.ensure_consistent_state()
            departments = await self.group_loader.read()
            schedules = await self.default_schedule_loader.read()
            subscriptions = await self.subscribe_loader.read()
            groups_changed = await self.group_loader.load(departments)
            group_names = {group.name for department in departments for group in department.groups}
            schedules_changed = await self.default_schedule_loader.load(schedules, group_names)
            subscribes_changed = await self.subscribe_loader.load(subscriptions)

        if groups_changed:
            await cache.delete_tags("groups", "departments")
        if schedules_changed:
            await cache.delete_tags("default-schedules")
        if subscribes_changed:
            await cache.delete_tags("subscribes")
