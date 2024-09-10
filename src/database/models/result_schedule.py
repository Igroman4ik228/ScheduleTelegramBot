from base import Base, group_foreign_key, int_pk, str_512
from sqlalchemy.orm import Mapped


class ResultScheduleModel(Base):
    __tablename__ = 'ResultSchedule'

    id = Mapped[int_pk]
    weekday = Mapped[int]
    data_lesson = Mapped[str_512]
    group_id = Mapped[group_foreign_key]
