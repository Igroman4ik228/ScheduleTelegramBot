from sqlalchemy.orm import Mapped, relationship

from database.models.base import Base, group_foreign_key, str_1024


class ResultScheduleModel(Base):
    __tablename__ = 'ResultSchedule'

    weekday: Mapped[int]
    data_lessons: Mapped[str_1024]
    group_id: Mapped[group_foreign_key]

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
