from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, BoolFalse, BoolTrue, CreatedAt, Str128

if TYPE_CHECKING:
    from database.models import GroupModel, SubscribeModel


class UserModel(Base):
    first_name: Mapped[Str128]
    last_name: Mapped[Str128 | None]
    user_name: Mapped[Str128 | None]
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    subscribe_end_time: Mapped[datetime | None]
    count_referral: Mapped[int] = mapped_column(default=0)

    is_bot: Mapped[BoolFalse]
    is_premium: Mapped[BoolFalse]
    is_time_shown: Mapped[BoolTrue]
    is_notify: Mapped[BoolTrue]
    is_ban: Mapped[BoolFalse]

    group_id: Mapped[int | None] = mapped_column(
        ForeignKey("Groups.id", ondelete="SET NULL")
    )
    subscribe_id: Mapped[int | None] = mapped_column(
        ForeignKey("Subscribes.id", ondelete="SET NULL")
    )

    group: Mapped[GroupModel] = relationship(back_populates="users")
    subscribe: Mapped[SubscribeModel] = relationship(back_populates="users")

    created_at: Mapped[CreatedAt]

    def get_full_name(self):
        if self.last_name is None:
            return self.first_name
        return f"{self.first_name} {self.last_name}"
