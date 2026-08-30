from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from scheduletelegrambot.database.models.base import BaseModel, Str8192
from scheduletelegrambot.enums import Weekday

if TYPE_CHECKING:
    from scheduletelegrambot.database.models import GroupModel


class ResultScheduleModel(BaseModel):
    __table_args__ = (UniqueConstraint("group_id", "weekday", name="uq_result_schedules_period"),)

    weekday: Mapped[Weekday] = mapped_column(
        Enum(
            Weekday,
            values_callable=lambda enum: [member.value for member in enum],
            native_enum=True,
            name="weekday",
        )
    )
    data_lessons: Mapped[Str8192]
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), index=True)

    group: Mapped[GroupModel] = relationship(back_populates="result_schedule")
