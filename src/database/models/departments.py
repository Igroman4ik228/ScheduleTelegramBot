from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base, int_pk, str_128


class DepartmentModel(Base):
    __tablename__ = 'Departments'

    id: Mapped[int_pk]
    name: Mapped[str_128] = mapped_column(unique=True)

    groups: Mapped[list["GroupModel"]] = relationship(
        back_populates="department"
    )
