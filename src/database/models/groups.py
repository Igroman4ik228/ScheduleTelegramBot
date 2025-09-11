from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import BaseModel, Str128

if TYPE_CHECKING:
    from database.models import (
        DefaultScheduleModel,
        DepartmentModel,
        ResultScheduleModel,
        UserModel,
    )


class GroupModel(BaseModel):
    name: Mapped[Str128] = mapped_column(unique=True)
    department_id: Mapped[int] = mapped_column(
        ForeignKey("Departments.id", ondelete="CASCADE")
    )
    global_shift: Mapped[int] = mapped_column(
        default=1
    )  # Смена для всех групп (первая или вторая)

    department: Mapped[DepartmentModel] = relationship(back_populates="groups")

    users: Mapped[list[UserModel]] = relationship(back_populates="group")
    default_schedule: Mapped[list[DefaultScheduleModel]] = relationship(
        back_populates="group"
    )
    result_schedule: Mapped[list[ResultScheduleModel]] = relationship(
        back_populates="group"
    )
