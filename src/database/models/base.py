import datetime
from typing import Annotated

from sqlalchemy import ForeignKey, String, text
from sqlalchemy.orm import DeclarativeBase, mapped_column

int_pk = Annotated[int, mapped_column(primary_key=True)]

created_at = Annotated[datetime.datetime, mapped_column(
    server_default=text("TIMEZONE('utc', now())")
)]

group_foreign_key = Annotated[int, mapped_column(
    ForeignKey("Groups.id", ondelete="CASCADE")
)]

department_foreign_key = Annotated[int, mapped_column(
    ForeignKey("Departments.id", ondelete="CASCADE")
)]

str_256 = Annotated(str, 256)
str_512 = Annotated(str, 512)


class Base(DeclarativeBase):
    type_annotation_map = {
        str_256: String(256),
        str_512: String(512)
    }

    repr_cols_num: int = 4  # print first columns
    repr_cols: tuple = ()  # extra printed columns

    def __repr__(self) -> str:
        cols = [
            f"{col}={getattr(self, col)}"
            for idx, col in enumerate(self.__table__.columns.keys())
            if col in self.repr_cols or idx < self.repr_cols_num
        ]
        return f"<{self.__class__.__name__} {', '.join(cols)}>"
