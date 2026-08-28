from __future__ import annotations

from scheduletelegrambot.schemas.base import BaseSchema
from scheduletelegrambot.schemas.department import DepartmentBaseSchema


class GroupBaseSchema(BaseSchema):
    id: int
    name: str
    department_id: int
    global_shift: int

class GroupWithDepartmentSchema(GroupBaseSchema):
    department: DepartmentBaseSchema
