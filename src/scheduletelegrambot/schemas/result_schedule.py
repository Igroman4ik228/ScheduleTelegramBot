from __future__ import annotations

from scheduletelegrambot.schemas.base import BaseSchema
from scheduletelegrambot.schemas.group import GroupBaseSchema


class ResultScheduleBaseSchema(BaseSchema):
    id: int
    weekday: int
    data_lessons: str
    group_id: int

class ResultScheduleWithGroupSchema(ResultScheduleBaseSchema):
    group: GroupBaseSchema
