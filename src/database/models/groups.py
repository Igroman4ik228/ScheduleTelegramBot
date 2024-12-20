from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, Str128


class GroupModel(Base):
    name: Mapped[Str128] = mapped_column(unique=True)
    department_id: Mapped[int] = mapped_column(
        ForeignKey("Departments.id",
                   ondelete="CASCADE")
    )

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
