from __future__ import annotations

from scheduletelegrambot.schemas.base import BaseSchema


class DepartmentBaseSchema(BaseSchema):
    id: int
    name: str

class DepartmentCreateSchema(BaseSchema):
    name: str
