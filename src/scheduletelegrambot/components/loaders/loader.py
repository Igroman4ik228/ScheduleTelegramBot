from scheduletelegrambot.components.loaders.default_schedule import (
    DefaultScheduleLoader,
)
from scheduletelegrambot.components.loaders.groups import GroupLoader
from scheduletelegrambot.components.loaders.subscriptions import SubscribeLoader


class InitialDataLoader:
    def __init__(
        self,
        group_loader: GroupLoader,
        subscribe_loader: SubscribeLoader,
        default_schedule_loader: DefaultScheduleLoader,
    ) -> None:
        self.group_loader = group_loader
        self.subscribe_loader = subscribe_loader
        self.default_schedule_loader = default_schedule_loader

    async def load(self) -> None:
        await self.group_loader.load()
        await self.subscribe_loader.load()
        await self.default_schedule_loader.load()
