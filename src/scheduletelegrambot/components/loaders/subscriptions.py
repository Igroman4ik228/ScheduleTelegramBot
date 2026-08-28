from pathlib import Path
from typing import Any

from pydantic import BaseModel

from scheduletelegrambot.database.repositories.subscribes import SubscribeRepository
from scheduletelegrambot.database.uow import UoW
from scheduletelegrambot.helpers.file import get_file_paths, load_from_json
from scheduletelegrambot.utils.constants import FILE_EXTENSION

from .paths import SUBSCRIPTIONS_DIR


class InitialSubscription(BaseModel):
    name: str
    description: str | None = None
    duration_days: int
    price: int
    can_referral: bool = True
    discount: int | None = None


class SubscribeLoader:
    def __init__(self, subscriptions: SubscribeRepository, uow: UoW) -> None:
        self.subscriptions = subscriptions
        self.uow = uow

    async def load(self) -> None:
        file_paths = get_file_paths(SUBSCRIPTIONS_DIR, FILE_EXTENSION)
        subscriptions = await self._read_subscriptions(file_paths)
        is_changed = False

        for subscription in subscriptions:
            if await self.subscriptions.get_by_name(subscription.name) is not None:
                continue

            await self.subscriptions.create(**subscription.model_dump())
            is_changed = True

        if is_changed:
            await self.uow.commit()

    async def _read_subscriptions(self, file_paths: list[Path]) -> list[InitialSubscription]:
        subscriptions = []
        for file_path in file_paths:
            data: Any = await load_from_json(str(file_path))
            records = data if isinstance(data, list) else [data]
            subscriptions.extend(InitialSubscription.model_validate(record) for record in records)

        return subscriptions
