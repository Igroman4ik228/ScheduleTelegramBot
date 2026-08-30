from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from scheduletelegrambot.database.models import SubscribeModel
from scheduletelegrambot.helpers.file import get_file_paths, load_from_json
from scheduletelegrambot.utils.constants import FILE_EXTENSION

from .paths import SUBSCRIPTIONS_DIR


class InitialSubscription(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str | None = None
    duration_days: int
    price: int
    can_referral: bool = True
    discount: int | None = None


class SubscribeLoader:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def read(self) -> list[InitialSubscription]:
        subscriptions: list[InitialSubscription] = []
        for path in get_file_paths(SUBSCRIPTIONS_DIR, FILE_EXTENSION):
            data = await load_from_json(str(path))
            records = data if isinstance(data, list) else [data]
            subscriptions.extend(InitialSubscription.model_validate(record) for record in records)
        return subscriptions

    async def load(self, subscriptions: list[InitialSubscription]) -> bool:
        if await self.session.scalar(SubscribeModel.__table__.select().limit(1)) is not None:
            return False
        self.session.add_all(
            SubscribeModel(**subscription.model_dump()) for subscription in subscriptions
        )
        await self.session.flush()
        return bool(subscriptions)
