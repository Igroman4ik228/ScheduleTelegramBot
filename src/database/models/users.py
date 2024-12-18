from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, BoolFalse, BoolTrue, CreatedAt, Str128


class UserModel(Base):
    first_name: Mapped[Str128]
    last_name: Mapped[Str128 | None]
    user_name: Mapped[Str128]
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True
    )
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

    group: Mapped["GroupModel"] = relationship(
        back_populates="users"
    )
    subscribe: Mapped["SubscribeModel"] = relationship(
        back_populates="users"
    )

    created_at: Mapped[CreatedAt]

    def __repr__(self):
        return (
            "User(\n"
            f"id={self.id!r},\n"
            f"first_name={self.first_name!r},\n"
            f"last_name={self.last_name!r},\n"
            f"user_name={self.user_name!r},\n"
            f"telegram_id={self.telegram_id!r},\n"
            f"group_id={self.group_id!r},\n"
            f"is_bot={self.is_bot!r},\n"
            f"is_time_shown={self.is_time_shown!r},\n"
            f"is_notify={self.is_notify!r},\n"
            f"is_ban={self.is_ban!r},\n"
            f"is_premium={self.is_premium!r},\n"
            f"CreatedAt={self.CreatedAt!r}\n"
            ")"
        )

    def __str__(self):
        last_name_str = f" {self.last_name}" if self.last_name else ""
        return (
            "\n"
            "User Information:\n"
            f"  Name: {self.first_name} {last_name_str}\n"
            f"  Username: @{self.user_name}\n"
            f"  Telegram ID: {self.telegram_id}\n"
            f"  Group ID: {self.group_id}\n"
            f"  Banned: {'Yes' if self.is_ban else 'No'}"
        )
