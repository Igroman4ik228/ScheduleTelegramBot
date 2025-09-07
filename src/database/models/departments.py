from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, Str128

if TYPE_CHECKING:
    from database.models import GroupModel


class DepartmentModel(Base):
    name: Mapped[Str128] = mapped_column(unique=True)

    groups: Mapped[list[GroupModel]] = relationship(back_populates="department")
