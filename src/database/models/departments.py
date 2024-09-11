from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, int_pk, str_256


class DepartmentModel(Base):
    __tablename__ = 'Departments'

    id: Mapped[int_pk]
    name: Mapped[str_256] = mapped_column(unique=True)

    groups: Mapped[list["GroupModel"]] = relationship(
        back_populates="department"
    )
