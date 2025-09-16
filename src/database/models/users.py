from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import (
    BaseModel,
    BoolFalse,
    BoolTrue,
    Int64,
    Str128,
)
from database.models.mixins.timestamp import TimestampMixin

if TYPE_CHECKING:
    from database.models import GroupModel, SubscribeModel


class UserModel(BaseModel, TimestampMixin):
    first_name: Mapped[Str128]
    last_name: Mapped[Str128 | None]
    user_name: Mapped[Str128 | None]
    telegram_id: Mapped[Int64] = mapped_column(unique=True, index=True)
    subscribe_end_time: Mapped[datetime | None]
    count_referral: Mapped[int] = mapped_column(server_default=text("0"))

    is_bot: Mapped[BoolFalse]
    is_premium: Mapped[BoolFalse]
    is_time_shown: Mapped[BoolTrue]
    is_notify: Mapped[BoolTrue]
    is_ban: Mapped[BoolFalse]

    group_id: Mapped[int | None] = mapped_column(
        ForeignKey("groups.id", ondelete="SET NULL")
    )
    subscribe_id: Mapped[int | None] = mapped_column(
        ForeignKey("subscribes.id", ondelete="SET NULL")
    )

    group: Mapped[GroupModel | None] = relationship(back_populates="users")
    subscribe: Mapped[SubscribeModel | None] = relationship(
        back_populates="users"
    )

    @property
    def full_name(self):
        if self.last_name is None:
            return self.first_name
        return f"{self.first_name} {self.last_name}"
