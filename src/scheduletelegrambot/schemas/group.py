from __future__ import annotations

from scheduletelegrambot.enums import StudyShift
from scheduletelegrambot.schemas.base import BaseSchema
from scheduletelegrambot.schemas.department import DepartmentBaseSchema


class GroupBaseSchema(BaseSchema):
    id: int
    name: str
    department_id: int
    study_shift: StudyShift


class GroupWithDepartmentSchema(GroupBaseSchema):
    department: DepartmentBaseSchema
