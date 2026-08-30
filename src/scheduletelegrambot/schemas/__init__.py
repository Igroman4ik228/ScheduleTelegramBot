from .base import BaseSchema
from .default_schedule import (
    ClassroomSchema,
    DefaultScheduleBaseSchema,
    DefaultScheduleLessonSchema,
    DefaultScheduleWithGroupSchema,
    SubjectSchema,
    TeacherSchema,
    TeachingAssignmentClassroomSchema,
    TeachingAssignmentSchema,
)
from .department import DepartmentBaseSchema, DepartmentCreateSchema
from .group import GroupBaseSchema, GroupWithDepartmentSchema
from .referral import ReferralBaseSchema, ReferralWithUsersSchema
from .result_schedule import ResultScheduleBaseSchema, ResultScheduleWithGroupSchema
from .subscribe import SubscribeBaseSchema
from .user import UserBaseSchema, UserWithAllSchema, UserWithGroupSchema

__all__ = (
    "BaseSchema",
    "ClassroomSchema",
    "DefaultScheduleBaseSchema",
    "DefaultScheduleLessonSchema",
    "DefaultScheduleWithGroupSchema",
    "DepartmentBaseSchema",
    "DepartmentCreateSchema",
    "GroupBaseSchema",
    "GroupWithDepartmentSchema",
    "ReferralBaseSchema",
    "ReferralWithUsersSchema",
    "ResultScheduleBaseSchema",
    "ResultScheduleWithGroupSchema",
    "SubjectSchema",
    "SubscribeBaseSchema",
    "TeacherSchema",
    "TeachingAssignmentClassroomSchema",
    "TeachingAssignmentSchema",
    "UserBaseSchema",
    "UserWithAllSchema",
    "UserWithGroupSchema",
)
