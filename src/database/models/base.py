from datetime import datetime
from typing import Annotated

from sqlalchemy import String, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

Pk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]

BoolTrue = Annotated[bool, mapped_column(server_default=text("true"))]
BoolFalse = Annotated[bool, mapped_column(server_default=text("false"))]

CreatedAt = Annotated[datetime, mapped_column(server_default=func.now())]
UpdatedAt = Annotated[
    datetime,
    mapped_column(server_default=func.now(), server_onupdate=func.now()),
]

Str128 = Annotated[str, 128]
Str512 = Annotated[str, 512]
Str1024 = Annotated[str, 1024]
Str2048 = Annotated[str, 2048]
Str8192 = Annotated[str, 8192]


class BaseModel(DeclarativeBase):
    id: Mapped[Pk]

    type_annotation_map = {
        Str128: String(128),
        Str512: String(512),
        Str1024: String(1024),
        Str2048: String(2048),
        Str8192: String(8192),
    }

    # Tables name
    @declared_attr.directive
    def __tablename__(self) -> str:
        return f"{self.__name__[:-5]}s"

    repr_cols_num: int = 4  # print first columns (don't count id)
    repr_cols: tuple[str,] = ()  # extra printed columns

    def __repr__(self) -> str:
        cols = [f"id={self.id}"]
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col == "id":
                continue
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")
        return f"<{self.__class__.__name__} {', '.join(cols)}>"
