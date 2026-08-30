from .catalogs import ClassroomModel, SubjectModel, TeacherModel
from .default_schedule import (
    DefaultScheduleAssignmentClassroomModel,
    DefaultScheduleLessonModel,
    DefaultScheduleModel,
    DefaultScheduleTeachingAssignmentModel,
)
from .departments import DepartmentModel
from .groups import GroupModel
from .referrals import ReferralModel
from .result_schedule import ResultScheduleModel
from .subscribe import SubscribeModel
from .users import UserModel

__all__ = (
    "ClassroomModel",
    "DefaultScheduleAssignmentClassroomModel",
    "DefaultScheduleLessonModel",
    "DefaultScheduleModel",
    "DefaultScheduleTeachingAssignmentModel",
    "DepartmentModel",
    "GroupModel",
    "ReferralModel",
    "ResultScheduleModel",
    "SubjectModel",
    "SubscribeModel",
    "TeacherModel",
    "UserModel",
)
