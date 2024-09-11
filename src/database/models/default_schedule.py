from sqlalchemy.orm import Mapped, relationship

from database.models.base import Base, group_foreign_key, int_pk, str_512


class DefaultScheduleModel(Base):
    __tablename__ = 'DefaultSchedule'

    id: Mapped[int_pk]
    shift: Mapped[int]
    weekday: Mapped[int]
    data_lessons: Mapped[str_512]
    group_id: Mapped[group_foreign_key]

    group: Mapped["GroupModel"] = relationship(
        back_populates="default_schedule"
    )
