import time
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Update

from database.db import sessionmaker
from database.repositories.default_schedule import DefaultScheduleRepository
from database.repositories.departments import DepartmentRepository
from database.repositories.groups import GroupRepository
from database.repositories.result_schedule import ResultScheduleRepository
from database.repositories.users import UserRepository


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        async with sessionmaker() as session:
            data["user_rep"] = UserRepository(session)
            data["result_schedule_rep"] = ResultScheduleRepository(session)
            data["group_rep"] = GroupRepository(session)
            data["default_schedule_rep"] = DefaultScheduleRepository(session)
            data["department_rep"] = DepartmentRepository(session)

            return await handler(event, data)
