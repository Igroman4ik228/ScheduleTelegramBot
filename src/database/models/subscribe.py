from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from database.models.base import BaseModel, BoolTrue, Str128, Str512

if TYPE_CHECKING:
    from database.models import UserModel


class SubscribeModel(BaseModel):
    name: Mapped[Str128]
    description: Mapped[Str512 | None]
    duration_days: Mapped[int]
    price: Mapped[int]
    can_referral: Mapped[BoolTrue]
    discount: Mapped[int | None]  # in percent

    users: Mapped[list[UserModel]] = relationship(back_populates="subscribe")
