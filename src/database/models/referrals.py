from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import BaseModel

if TYPE_CHECKING:
    from database.models import (
        UserModel,
    )


class ReferralModel(BaseModel):
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("Users.telegram_id", ondelete="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("Users.telegram_id", ondelete="CASCADE"), unique=True
    )

    owner: Mapped[UserModel] = relationship(foreign_keys=[owner_id])
    user: Mapped[UserModel] = relationship(foreign_keys=[user_id])
