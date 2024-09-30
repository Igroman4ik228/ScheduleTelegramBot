from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import (Base, bool_false, bool_true, created_at,
                                  int_pk, str_128)


class UserModel(Base):
    __tablename__ = 'Users'

    id: Mapped[int_pk]
    first_name: Mapped[str_128]
    last_name: Mapped[str_128 | None]
    user_name: Mapped[str_128]
    telegram_id: Mapped[int] = mapped_column(unique=True)

    group_id: Mapped[int | None] = mapped_column(
        ForeignKey("Groups.id", ondelete="CASCADE")
    )

    is_bot: Mapped[bool_false]
    is_time_shown: Mapped[bool_true]
    is_notify: Mapped[bool_true]
    is_ban: Mapped[bool_false]
    is_premium: Mapped[bool_false]

    group: Mapped["GroupModel"] = relationship(
        back_populates="users"
    )

    created_at: Mapped[created_at]

    # todo: __str__f) -> str_128
    # def __str__(sel:
    #     return super().__str__()
