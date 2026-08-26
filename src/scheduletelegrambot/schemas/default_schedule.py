from __future__ import annotations

from pydantic import AliasChoices, AliasPath, Field

from scheduletelegrambot.schemas.base import BaseSchema


class DefaultScheduleBaseSchema(BaseSchema):
    id: int
    weekday: int
    shift: int
    data_lessons: str
    group_id: int


class DefaultScheduleCreateSchema(BaseSchema):
    weekday: int
    shift: int
    data_lessons: str
    group_name: str


class DefaultScheduleWithGroupSchema(DefaultScheduleBaseSchema):
    group_name: str = Field(
        validation_alias=AliasChoices("group_name", AliasPath("group", "name"))
    )


class DefaultScheduleUpdateSchema(BaseSchema):
    id: int
    data_lessons: str
