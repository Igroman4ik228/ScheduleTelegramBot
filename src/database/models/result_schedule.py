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

    def __repr__(self):
        return (
            "ResultSchedule(\n"
            f"id={self.id!r},\n"
            f"weekday={self.weekday!r},\n"
            f"data_lessons={self.data_lessons!r},\n"
            f"group_id={self.group_id!r},\n"
            ")"
        )

    def __str__(self):
        return (
            "\n"
            "Result Schedule Information:\n"
            f"  Weekday: {self.weekday}\n"
            f"  Data Lessons: {self.data_lessons}\n"
            f"  Group ID: {self.group_id}\n"
        )
