from __future__ import annotations

from datetime import datetime

from scheduletelegrambot.schemas.base import BaseSchema
from scheduletelegrambot.schemas.group import GroupBaseSchema
from scheduletelegrambot.schemas.subscribe import SubscribeBaseSchema


class UserBaseSchema(BaseSchema):
    id: int
    first_name: str
    last_name: str | None
    user_name: str | None
    telegram_id: int
    subscribe_end_time: datetime | None
    count_referral: int
    is_bot: bool
    is_premium: bool
    is_time_shown: bool
    is_notify: bool
    is_ban: bool
    group_id: int | None
    subscribe_id: int | None

    @property
    def full_name(self) -> str:
        if self.last_name is None:
            return self.first_name
        return f"{self.first_name} {self.last_name}"

class UserWithGroupSchema(UserBaseSchema):
    group: GroupBaseSchema | None

class UserWithAllSchema(UserWithGroupSchema):
    subscribe: SubscribeBaseSchema | None
