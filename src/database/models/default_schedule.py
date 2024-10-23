from sqlalchemy.orm import Mapped, relationship

from database.models.base import Base, group_foreign_key, str_512


class DefaultScheduleModel(Base):
    __tablename__ = 'DefaultSchedule'

    weekday: Mapped[int]
    shift: Mapped[int]
    data_lessons: Mapped[str_512]
    group_id: Mapped[group_foreign_key]

    group: Mapped["GroupModel"] = relationship(
        back_populates="default_schedule", lazy="selectin"
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
