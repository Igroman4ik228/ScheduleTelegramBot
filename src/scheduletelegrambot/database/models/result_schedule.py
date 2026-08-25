from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from scheduletelegrambot.database.models.base import BaseModel, Str8192

if TYPE_CHECKING:
    from scheduletelegrambot.database.models import GroupModel


class ResultScheduleModel(BaseModel):
    weekday: Mapped[int]
    data_lessons: Mapped[Str8192]
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))

    group: Mapped[GroupModel] = relationship(back_populates="result_schedule")
