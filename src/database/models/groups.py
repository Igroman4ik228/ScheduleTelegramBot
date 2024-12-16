from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, department_foreign_key, str_128


class GroupModel(Base):
    name: Mapped[str_128] = mapped_column(unique=True)
    department_id: Mapped[department_foreign_key]

    department: Mapped["DepartmentModel"] = relationship(
        back_populates="groups", lazy="selectin"
    )

    users: Mapped[list["UserModel"]] = relationship(
        back_populates="group", lazy="selectin"
    )
    default_schedule: Mapped[list["DefaultScheduleModel"]] = relationship(
        back_populates="group", lazy="selectin"
    )
    result_schedule: Mapped[list["ResultScheduleModel"]] = relationship(
        back_populates="group", lazy="selectin"
    )

    def __repr__(self):
        return (
            "Group(\n"
            f"id={self.id!r},\n"
            f"name={self.name!r},\n"
            f"department_id={self.department_id!r},\n"
            ")"
        )

    def __str__(self):
        return (
            "\n"
            "Group Information:\n"
            f"  Name: {self.name}\n"
            f"  Department ID: {self.department_id}\n"
            f"  Number of Users: {len(self.users)}\n"
            f"  Number of Default Schedules: {len(self.default_schedule)}\n"
            f"  Number of Result Schedules: {len(self.result_schedule)}\n"
        )
