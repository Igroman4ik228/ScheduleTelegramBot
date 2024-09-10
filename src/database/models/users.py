from base import Base, created_at, group_foreign_key, int_pk, str_256
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UserModel(Base):
    __tablename__ = 'Users'

    id = Mapped[int_pk]
    name = Mapped[str_256]
    telegram_id = Mapped[int]
    group_id = Mapped[group_foreign_key]
    created_at = Mapped[created_at]

    is_time_shown = Mapped[bool] = mapped_column(default=True)
    is_notify = Mapped[bool] = mapped_column(default=True)
    is_ban = Mapped[bool] = mapped_column(default=False)

    group: Mapped["GroupModel"] = relationship()
