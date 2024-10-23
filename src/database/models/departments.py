from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, str_128


class DepartmentModel(Base):
    __tablename__ = 'Departments'

    name: Mapped[str_128] = mapped_column(unique=True)

    groups: Mapped[list["GroupModel"]] = relationship(
        back_populates="department", lazy="selectin"
    )

    def __repr__(self):
        return (
            "Department(\n"
            f"id={self.id!r},\n"
            f"name={self.name!r},\n"
            ")"
        )

    def __str__(self):
        return (
            "\n"
            "Department Information:\n"
            f"  Name: {self.name}\n"
            f"  Number of Groups: {len(self.groups)}\n"
        )
