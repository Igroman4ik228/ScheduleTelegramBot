from __future__ import annotations

from scheduletelegrambot.enums import Weekday, WeekType
from scheduletelegrambot.schemas.base import BaseSchema
from scheduletelegrambot.schemas.group import GroupBaseSchema


class TeacherSchema(BaseSchema):
    id: int
    name: str


class SubjectSchema(BaseSchema):
    id: int
    name: str


class ClassroomSchema(BaseSchema):
    id: int
    name: str


class TeachingAssignmentClassroomSchema(BaseSchema):
    id: int
    classroom: ClassroomSchema


class TeachingAssignmentSchema(BaseSchema):
    id: int
    teacher: TeacherSchema
    classrooms: list[TeachingAssignmentClassroomSchema]


class DefaultScheduleLessonSchema(BaseSchema):
    id: int
    number: int
    subject: SubjectSchema
    teaching_assignments: list[TeachingAssignmentSchema]


class DefaultScheduleBaseSchema(BaseSchema):
    id: int
    weekday: Weekday
    week_type: WeekType
    group_id: int
    lessons: list[DefaultScheduleLessonSchema]


class DefaultScheduleWithGroupSchema(DefaultScheduleBaseSchema):
    group: GroupBaseSchema
