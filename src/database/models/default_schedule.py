from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, Str2048


class DefaultScheduleModel(Base):
    weekday: Mapped[int]
    shift: Mapped[int]
    data_lessons: Mapped[Str2048]
    group_id: Mapped[int] = mapped_column(
        ForeignKey("Groups.id",
                   ondelete="CASCADE")
    )

    group: Mapped["GroupModel"] = relationship(
        back_populates="default_schedule"
    )

    def __repr__(self):
        return (
            "DefaultSchedule(\n"
            f"id={self.id!r},\n"
            f"weekday={self.weekday!r},\n"
            f"shift={self.shift!r},\n"
            f"data_lessons={self.data_lessons!r},\n"
            f"group_id={self.group_id!r},\n"
            ")"
        )

    def __str__(self):
        return (
            "\n"
            "Default Schedule Information:\n"
            f"  Weekday: {self.weekday}\n"
            f"  Shift: {self.shift}\n"
            f"  Data Lessons: {self.data_lessons}\n"
            f"  Group ID: {self.group_id}\n"
        )
