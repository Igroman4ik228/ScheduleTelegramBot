from base import Base, department_foreign_key, int_pk, str_256
from sqlalchemy.orm import Mapped, relationship


class GroupModel(Base):
    __tablename__ = 'Groups'

    id = Mapped[int_pk]
    name = Mapped[str_256]
    department_id = Mapped[department_foreign_key]

    users: Mapped[list["UserModel"]] = relationship()
    department: Mapped["DepartmentModel"] = relationship()
