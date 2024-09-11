from sqlalchemy.orm import Mapped, relationship

from database.models.base import Base, group_foreign_key, int_pk, str_512


class ResultScheduleModel(Base):
    __tablename__ = 'ResultSchedule'

    id: Mapped[int_pk]
    weekday: Mapped[int]
    data_lessons: Mapped[str_512]
    group_id: Mapped[group_foreign_key]

    group: Mapped["GroupModel"] = relationship(
        back_populates="result_schedule"
    )
