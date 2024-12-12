from datetime import datetime
from typing import Annotated

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

int_pk = Annotated[int, mapped_column(primary_key=True)]

bool_false = Annotated[bool, mapped_column(default=False)]
bool_true = Annotated[bool, mapped_column(default=True)]

created_at = Annotated[
    datetime,
    mapped_column(default=datetime.now())
]

group_foreign_key = Annotated[int, mapped_column(
    ForeignKey("Groups.id", ondelete="CASCADE")
)]

department_foreign_key = Annotated[int, mapped_column(
    ForeignKey("Departments.id")
)]

str_128 = Annotated[str, 128]
str_512 = Annotated[str, 512]
str_1024 = Annotated[str, 1024]
str_2048 = Annotated[str, 2048]
str_8192 = Annotated[str, 8192]


class Base(DeclarativeBase):
    id: Mapped[int_pk]

    type_annotation_map = {
        str_128: String(128),
        str_512: String(512),
        str_1024: String(1024),
        str_2048: String(2048),
        str_8192: String(8192)
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
