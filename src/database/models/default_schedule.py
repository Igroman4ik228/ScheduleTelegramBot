from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, Str2048

if TYPE_CHECKING:
    from database.models import GroupModel


class DefaultScheduleModel(Base):
    weekday: Mapped[int]
    shift: Mapped[int]
    data_lessons: Mapped[Str2048]
    group_id: Mapped[int] = mapped_column(
        ForeignKey("Groups.id", ondelete="CASCADE")
    )

    group: Mapped[GroupModel] = relationship(back_populates="default_schedule")
