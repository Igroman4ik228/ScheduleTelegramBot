from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, Str8192


class ResultScheduleModel(Base):
    weekday: Mapped[int]
    data_lessons: Mapped[Str8192]
    group_id: Mapped[int] = mapped_column(
        ForeignKey("Groups.id", ondelete="CASCADE")
    )

    group: Mapped["GroupModel"] = relationship(
        back_populates="result_schedule"
    )
