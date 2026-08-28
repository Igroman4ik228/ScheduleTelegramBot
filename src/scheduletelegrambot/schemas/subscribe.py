from __future__ import annotations

from scheduletelegrambot.schemas.base import BaseSchema


class SubscribeBaseSchema(BaseSchema):
    id: int
    name: str
    description: str | None
    duration_days: int
    price: int
    can_referral: bool
    discount: int | None
