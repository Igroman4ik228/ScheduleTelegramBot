from base import Base, int_pk, str_256
from sqlalchemy.orm import Mapped, relationship


class DepartmentModel(Base):
    __tablename__ = 'Departments'

    id = Mapped[int_pk]
    name = Mapped[str_256]

    groups: Mapped[list["GroupModel"]] = relationship()
