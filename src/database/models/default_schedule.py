from base import Base, group_foreign_key, int_pk, str_512
from sqlalchemy.orm import Mapped, relationship


class DefaultScheduleModel(Base):
    __tablename__ = 'DefaultSchedule'

    id = Mapped[int_pk]
    week_schedule = Mapped[int]
    weekday = Mapped[int]
    data_lessons = Mapped[str_512]
    group_id = Mapped[group_foreign_key]

    group: Mapped["GroupModel"] = relationship()
