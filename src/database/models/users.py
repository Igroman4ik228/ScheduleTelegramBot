from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import (Base, bool_false, bool_true, created_at,
                                  str_128)


class UserModel(Base):
    __tablename__ = 'Users'

    first_name: Mapped[str_128]
    last_name: Mapped[str_128 | None]
    user_name: Mapped[str_128]
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True
    )

    group_id: Mapped[int | None] = mapped_column(
        ForeignKey("Groups.id", ondelete="CASCADE")
    )
    subscribe_id: Mapped[int | None] = mapped_column(
        ForeignKey("Subscribes.id", ondelete="CASCADE")
    )

    is_bot: Mapped[bool_false]
    is_time_shown: Mapped[bool_true]
    is_notify: Mapped[bool_true]
    is_ban: Mapped[bool_false]
    is_premium: Mapped[bool_false]

    group: Mapped["GroupModel"] = relationship(
        back_populates="users"
    )
    subscribe: Mapped["SubscribeModel"] = relationship(
        back_populates="users"
    )

    created_at: Mapped[created_at]

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
            f"created_at={self.created_at!r}\n"
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
