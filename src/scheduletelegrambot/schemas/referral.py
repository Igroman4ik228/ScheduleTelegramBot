from __future__ import annotations

from scheduletelegrambot.schemas.base import BaseSchema
from scheduletelegrambot.schemas.user import UserBaseSchema


class ReferralBaseSchema(BaseSchema):
    id: int
    owner_id: int
    user_id: int

class ReferralWithUsersSchema(ReferralBaseSchema):
    owner: UserBaseSchema
    user: UserBaseSchema
