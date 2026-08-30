from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from scheduletelegrambot.database.models.base import BaseModel, Str128
from scheduletelegrambot.enums import StudyShift

if TYPE_CHECKING:
    from scheduletelegrambot.database.models import (
        DefaultScheduleModel,
        DepartmentModel,
        ResultScheduleModel,
        UserModel,
    )


class GroupModel(BaseModel):
    name: Mapped[Str128] = mapped_column(unique=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id", ondelete="CASCADE"))
    study_shift: Mapped[StudyShift] = mapped_column(
        Enum(
            StudyShift,
            values_callable=lambda enum: [member.value for member in enum],
            native_enum=True,
            name="study_shift",
        ),
        server_default=text("'1'"),
    )

    department: Mapped[DepartmentModel] = relationship(back_populates="groups")

    users: Mapped[list[UserModel]] = relationship(back_populates="group")
    default_schedules: Mapped[list[DefaultScheduleModel]] = relationship(
        back_populates="group", cascade="all, delete-orphan", passive_deletes=True
    )
    result_schedule: Mapped[list[ResultScheduleModel]] = relationship(back_populates="group")
