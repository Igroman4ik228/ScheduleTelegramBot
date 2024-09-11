from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, created_at, int_pk, str_256


class UserModel(Base):
    __tablename__ = 'Users'

    id: Mapped[int_pk]
    name: Mapped[str_256]
    telegram_id: Mapped[int] = mapped_column(unique=True)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("Groups.id", ondelete="CASCADE"), nullable=True
    )
    created_at: Mapped[created_at]

    is_time_shown: Mapped[bool] = mapped_column(default=True)
    is_notify: Mapped[bool] = mapped_column(default=True)
    is_ban: Mapped[bool] = mapped_column(default=False)

    group: Mapped["GroupModel"] = relationship(
        back_populates="users"
    )

    # todo: __str__
    # def __str__(self) -> str_256:
    #     return super().__str__()
