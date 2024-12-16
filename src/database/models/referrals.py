from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class ReferralModel(Base):
    owner_id: Mapped[int] = mapped_column(
        ForeignKey('Users.telegram_id',
                   ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('Users.telegram_id',
                   ondelete="CASCADE"),
        unique=True
    )

    owner: Mapped["UserModel"] = relationship(
        foreign_keys=[owner_id], lazy="selectin"

    )
    user: Mapped["UserModel"] = relationship(
        foreign_keys=[user_id], lazy="selectin"
    )
