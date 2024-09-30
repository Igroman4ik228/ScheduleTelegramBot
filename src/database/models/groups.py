from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, department_foreign_key, int_pk, str_128


class GroupModel(Base):
    __tablename__ = 'Groups'

    id: Mapped[int_pk]
    name: Mapped[str_128] = mapped_column(unique=True)
    department_id: Mapped[department_foreign_key]

    department: Mapped["DepartmentModel"] = relationship(
        back_populates="groups"
    )

    users: Mapped[list["UserModel"]] = relationship(
        back_populates="group"
    )
    default_schedule: Mapped[list["DefaultScheduleModel"]] = relationship(
        back_populates="group"
    )
    result_schedule: Mapped[list["ResultScheduleModel"]] = relationship(
        back_populates="group"
    )
