from scheduletelegrambot.database.repositories.default_schedule import (
    DefaultScheduleRepository,
)
from scheduletelegrambot.database.repositories.departments import (
    DepartmentRepository,
)
from scheduletelegrambot.database.repositories.groups import GroupRepository
from scheduletelegrambot.database.repositories.referrals import (
    ReferralRepository,
)
from scheduletelegrambot.database.repositories.result_schedule import (
    ResultScheduleRepository,
)
from scheduletelegrambot.database.repositories.subscribes import (
    SubscribeRepository,
)
from scheduletelegrambot.database.repositories.users import UserRepository

__all__ = (
    "DefaultScheduleRepository",
    "DepartmentRepository",
    "GroupRepository",
    "ReferralRepository",
    "ResultScheduleRepository",
    "SubscribeRepository",
    "UserRepository",
)
